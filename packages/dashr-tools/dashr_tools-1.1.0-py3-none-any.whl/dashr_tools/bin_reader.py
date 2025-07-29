import struct

import pandas as pd
import numpy as np
import os
import glob
from natsort import natsorted
from tqdm import tqdm
from dashr_tools.dashr_data import DASHRMetadata, DASHRDataFile, DASHRData


def read_folder(folder_path: str) -> DASHRData:
    """Loads all data from a folder (and subfolders) and converts to a DASHRData object.

    :param folder_path: Folder path to raw .bin data
    :return: Converted DASHRData object
    :rtype: DASHRData
    """
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(folder_path)

    list_of_bins = natsorted(glob.glob(f"{folder_path}/**/*.BIN", recursive=True))
    dashr_data_files = [read_bin(x) for x in tqdm(list_of_bins)]
    dashr_data = DASHRData(dashr_data_files[0].metadata.device_type, dashr_data_files)
    return dashr_data


def read_single(filename: str) -> DASHRData:
    """Reads a single DASHR binary file and returns as a DASHRData object.

    :param filename: The filename of the DASHR binary file to read.
    :return: A DASHRData object containing the converted binary data.
    :rtype: DASHRData
    """
    data = read_bin(filename)
    return DASHRData(data.metadata.device_type, [data])


def read_bin(filename: str) -> DASHRDataFile:
    """Reads data from a single DASHR .bin file

    :param filename: The filename of the DASHR binary file to read.
    :return: A DASHRDataFile object containing the converted binary data and metadata.
    :rtype: DASHRDataFile
    """

    if ".bin" not in filename.lower():
        raise ValueError("File must be a .bin")
    if not os.path.exists(filename):
        raise FileNotFoundError("File does not exist")

    with open(filename, "rb") as f:
        f.seek(0, 2)  # jump to end
        end_position = f.tell()  # get size of file
        f.seek(0)  # go back to beginning

        header_data = f.read(512)
        file_metadata = process_header(header_data)
        file_data = []#np.empty((0,file_metadata.num_digital_channels), dtype=float)
        while f.tell() != end_position:
            current_data_segment = f.read(512)
            if len(current_data_segment) != 0:
                current_block = process_block(current_data_segment, file_metadata)
                file_data.append(current_block)#np.append(file_data, current_block)
        # file_data.reshape(file_data.shape[0]//file_metadata.num_digital_channels, file_metadata.num_digital_channels)
        file_data = np.concatenate(file_data)
    return DASHRDataFile(file_metadata, file_data)


def process_block(current_data_segment: bytes, file_metadata: DASHRMetadata) -> np.ndarray:
    """Reads and processes a block of data from the DASHR raw file format.

    Each 512 byte block contains a short 12-byte header section containing:

    +------+--------------------+----------------------------------------------------------------+----------+
    | Byte | Variable Name      | Description                                                    | Datatype |
    +======+====================+================================================================+==========+
    | 0-1  | data_block_count   | The number of data bytes in the block                          | uint32   |
    +------+--------------------+----------------------------------------------------------------+----------+
    | 2    | write_flag         | Flag to indicate if this block should be written to disk       | bool     |
    +------+--------------------+----------------------------------------------------------------+----------+
    | 3    | start_trigger_flag | Flag to indicate if this block was a 'triggering' block        | bool     |
    +------+--------------------+----------------------------------------------------------------+----------+
    | 4    | stop_trigger_flag  | Flag to indicate if this block was an 'end triggering' block   | bool     |
    +------+--------------------+----------------------------------------------------------------+----------+
    | 5-7  | trigger_count      | Incremental counter tracking how many blocks since the trigger | uint16   |
    +------+--------------------+----------------------------------------------------------------+----------+
    | 8-11 | millis_time        | Millisecond time of the LAST timestep in the block.            | uint32   |
    +------+--------------------+----------------------------------------------------------------+----------+

    :param current_data_segment: Raw data segment <bytes> from the DASHR raw file
    :param file_metadata: DASHR metadata from the DASHR raw file
    :return: DASHR data segment from the DASHR raw file, as a numpy array
    :rtype: np.ndarray
    """
    # The following metadata is extracted for completeness, but not required anywhere, and unused other than here.
    chunk_header = struct.unpack("HbbbHI", current_data_segment[:12])
    data_block_count = chunk_header[0]
    write_flag = chunk_header[1]
    start_trigger_flag = chunk_header[2]
    stop_trigger_flag = chunk_header[3]
    trigger_count = chunk_header[4]

    # Per the DynamicDataLogger git repository, this is the millisecond time of the LAST timestep in the block.
    millis_time = chunk_header[5]


    # The rest of the data line is processed here.
    data_end = divmod(500, file_metadata.pin_count * 2)[1]
    data_chunk = struct.unpack(f"{int((500 - data_end) / 2)}H", current_data_segment[12:-data_end])
    data_chunk = np.array(data_chunk, dtype='float').reshape(file_metadata.timesteps_per_block,
                                                             file_metadata.num_digital_channels)
    # Convert acceleration values
    if file_metadata.num_digital_channels == 9:
        data_chunk = nine_channel_read_line(data_chunk)
    elif file_metadata.num_digital_channels == 12:
        data_chunk = twelve_channel_read_line(data_chunk)
    else:
        raise ValueError(f"Unsupported number of sensor channels: {file_metadata.num_digital_channels}")

    return data_chunk


def convert_raw_temp(raw_value: np.ndarray, room_temp_offset: float = 25.0,
                     temp_sensitivity: float = 326.8) -> np.ndarray:
    value = (raw_value / temp_sensitivity) + room_temp_offset
    return value


def convert_raw_value(raw_value: np.ndarray, full_scale_range: int) -> np.ndarray:
    value = (raw_value - 32768.0) * (full_scale_range / 32768.0)
    return value


def twelve_channel_read_line(data: np.ndarray) -> np.ndarray:
    """Processes data from a single chunk of DASHR 12-axis data"""
    # Convert Acceleration Data (High Range)
    data[:, 0:3] = convert_raw_value(data[:, 0:3], 200)
    # Convert Acceleration Data (Low Range)
    data[:, 3:6] = convert_raw_value(data[:, 3:6], 32)
    # Convert Gyroscope Data
    data[:, 6:9] = convert_raw_value(data[:, 6:9], 4000)
    # Pass through pulse
    data[:, 9:11] = data[:, 9:11]
    # Convert Temperature data (from ICM-20601)
    data[:, 11] = convert_raw_temp(data[:, 11], 25, 326.8)

    return data


def nine_channel_read_line(data: np.array) -> np.array:
    """Processes data from a single chunk of DASHR 9-axis data"""
    # Convert Acceleration Data
    data[:, 0:3] = convert_raw_value(data[:, 0:3], 200)
    # Convert Gyroscope Data
    data[:, 3:6] = convert_raw_value(data[:, 3:6], 4000)
    # Pass through pulse/temperature
    data[:, 6:8] = data[:, 6:8]
    # Convert Temperature data (from ITG-3701)
    data[:, 8] = convert_raw_temp(data[:, 8], 21, 321.4)

    return data


def process_header(header: bytes) -> DASHRMetadata:
    """Parses header from DASHR .bin file

    DASHR header files follow the following structure:

    +---------+--------------------------+-----------------------------+----------+
    | Byte    | Variable Name            | Description                 | Datatype |
    +=========+==========================+=============================+==========+
    | 1-4     | count                    | 'Count'                     | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 5-8     | sample_frequency         | Sample Frequency            | int32    |
    +---------+--------------------------+-----------------------------+----------+
    | 9-12    | adc_resolution           | ADC Resolution              | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 13-16   | pin_count                | Pin Count                   | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 17-20   | trigger_index            | Trigger Index               | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 21-24   | timesteps_per_trigger    | Timesteps per Trigger       | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 25      | pretrigger_block_count   | Pretrigger Block Count      | raw      |
    +---------+--------------------------+-----------------------------+----------+
    | 29-32   | file_block_count         | File Block Count            | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 33-36   | timesteps_per_block      | Timesteps per Block         | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 37      | buffer_block_count       | Buffer Block Count          | raw      |
    +---------+--------------------------+-----------------------------+----------+
    | 38      | hardware_averaging_count | Hardware Averaging Count    | raw      |
    +---------+--------------------------+-----------------------------+----------+
    | 41-44   | trigger_time             | Trigger Time                | int32    |
    +---------+--------------------------+-----------------------------+----------+
    | 45      | trigger_sigma            | Trigger Sigma               | raw      |
    +---------+--------------------------+-----------------------------+----------+
    | 46      | num_digital_channels     | Number of Digital Channels  | raw      |
    +---------+--------------------------+-----------------------------+----------+
    | 47-70   | pin_number               | Pin Number                  | uint8    |
    +---------+--------------------------+-----------------------------+----------+
    | 71-118  | pin_avg                  | Pin Average                 | uint16   |
    +---------+--------------------------+-----------------------------+----------+
    | 121-216 | pin_std_dev              | Pin Standard Deviation      | single   |
    +---------+--------------------------+-----------------------------+----------+
    | 217-312 | pin_trigger_level        | Pin Trigger Level           | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 313-408 | pin_cal_factor           | Pin Calibration Factor      | single   |
    +---------+--------------------------+-----------------------------+----------+
    | 409-414 | mac                      | MAC Address (6 fields)      | hex      |
    +---------+--------------------------+-----------------------------+----------+
    | 417-420 | serial_number            | Serial Number               | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 421-422 | hw_rev                   | Hardware Revision           | uint16   |
    +---------+--------------------------+-----------------------------+----------+
    | 423-424 | sw_rev                   | Software Revision           | uint16   |
    +---------+--------------------------+-----------------------------+----------+
    | 425-430 | accel_bias               | Acceleration Bias, per axis | int16    |
    +---------+--------------------------+-----------------------------+----------+
    | 431-442 | cal_factors              | Calibration Factors         | uint16   |
    +---------+--------------------------+-----------------------------+----------+
    | 445-448 | last_cal_time            | Last Calibration Time       | uint32   |
    +---------+--------------------------+-----------------------------+----------+
    | 449-512 | empty                    | Empty values, ignore.       |          |
    +---------+--------------------------+-----------------------------+----------+

    """
    if len(header) != 512:
        raise ValueError("Header must be 512 bytes")

    if struct.unpack("I", header[0:4])[0] != 99:
        raise NotImplementedError("Invalid header. Recovery methods not yet implemented.")

    unpacked_header = struct.unpack('IiIIIIbIIbbibb24B24Hxx24f24I24f6BxxIHH3h6HxxI', header[0:448])

    metadata = DASHRMetadata(header, unpacked_header)

    return metadata


if __name__ == "__main__":
    filename = "Y:/AAAProjects/AtriumHSM/01_RawData/HSM0026/HDAM/1 STAR/0/L0.BIN"
    data_file = read_bin(filename)

    print(data_file)
