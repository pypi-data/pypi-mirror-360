import os
import struct
import numpy as np
import pandas as pd
import glob
from natsort import natsorted
from tqdm import tqdm

class DASHRMetadata:

    def __init__(self, raw_header: bytes, unpacked_header: tuple = (None)):
        """ Initialize DASHRMetadata from the raw `<bytes>`. Optionally provide unpacked header data.

        :param raw_header: Raw bytes of header section extracted from the DASHR .bin file.
        :param unpacked_header: Optional unpacked header section. If not provided, will use `raw_header` to unpack.


        :ivar str device_type: one of `nine-axis` or `twelve-axis`
        :ivar bytes raw_header: raw header data, in bytes
        :ivar tuple parsed_header: parsed header data
        :ivar int count:
        :ivar int sample_frequency:
        :ivar int adc_resolution:
        :ivar int pin_count:
        :ivar int trigger_index:
        :ivar int timesteps_per_trigger:
        :ivar int pretrigger_block_count:
        :ivar int file_block_count:
        :ivar int timesteps_per_block:
        :ivar int buffer_block_count:
        :ivar int hardware_averaging_count:
        :ivar int trigger_time:
        :ivar int trigger_sigma:
        :ivar int num_digital_channels:
        :ivar list[int] pin_number:
        :ivar list[int] pin_avg:
        :ivar list[float] pin_std:
        :ivar list[int] pin_trigger_level:
        :ivar list[float] pin_cal_factor:
        :ivar list[int] mac:
        :ivar int serial_number:
        :ivar int hw_rev:
        :ivar int sw_rev:
        :ivar list[int] accel_bias:
        :ivar list[int] cal_factors:
        :ivar int last_cal_time:

        """
        if len(raw_header) != 512:
            raise ValueError(f"DASHR header must be at least 512 bytes long: contains {len(raw_header)} bytes.")

        self.raw_header = raw_header
        if unpacked_header is not None:
            if len(unpacked_header) != 153:
                raise ValueError(f"Unpacked DASHR header must contain 153 elements: contains {len(unpacked_header)}.")
            #: Unpacked header structure
            self.unpacked_header = unpacked_header
        else:
            self.unpacked_header = struct.unpack('IiIIIIbIIbbibb24B24Hxx24f24I24f6BxxIHH3h6HxxI', raw_header[0:448])

        self.count = self.unpacked_header[0]
        self.sample_frequency = self.unpacked_header[1]
        self.adc_resolution = self.unpacked_header[2]
        self.pin_count = self.unpacked_header[3]
        self.trigger_index = self.unpacked_header[4]
        self.timesteps_per_trigger = self.unpacked_header[5]
        self.pretrigger_block_count = self.unpacked_header[6]
        self.file_block_count = self.unpacked_header[7]
        self.timesteps_per_block = self.unpacked_header[8]
        self.buffer_block_count = self.unpacked_header[9]
        self.hardware_averaging_count = self.unpacked_header[10]
        self.trigger_time = self.unpacked_header[11]
        self.trigger_sigma = self.unpacked_header[12]
        self.num_digital_channels = self.unpacked_header[13]
        self.pin_number = self.unpacked_header[14:38]
        self.pin_avg = self.unpacked_header[38:62]
        self.pin_std = self.unpacked_header[62:86]
        self.pin_trigger_level = self.unpacked_header[86:110]
        self.pin_cal_factor = self.unpacked_header[110:134]
        self.mac = self.unpacked_header[134:140]
        self.serial_number = self.unpacked_header[140]
        self.hw_rev = self.unpacked_header[141]
        self.sw_rev = self.unpacked_header[142]
        self.accel_bias = self.unpacked_header[143:146]
        self.cal_factors = self.unpacked_header[146:152]
        self.last_cal_time = self.unpacked_header[152]

        if self.num_digital_channels == 12:
            self.device_type = "twelve-axis"
        if self.num_digital_channels == 9:
            self.device_type = "nine-axis"


class DASHRDataFile:
    metadata: DASHRMetadata
    raw_data: np.ndarray
    filename: str

    def __init__(self, metadata: DASHRMetadata, raw_data: np.ndarray, filename: str = None):
        """

        :param metadata:
        :param raw_data:
        """
        self.metadata = metadata
        self.raw_data = raw_data
        if filename is not None:
            self.filename = filename

    def to_dataframe(self):
        if self.metadata.device_type.lower() == "twelve-axis":
            df = pd.DataFrame(self.raw_data[:,0:12], columns=["x_accel_hr", "y_accel_hr", "z_accel_hr",
                                                      "x_accel_lr", "y_accel_lr", "z_accel_lr",
                                                      "x_gyro", "y_gyro", "z_gyro",
                                                      "pulse", "ambient", "temperature"])
        elif self.metadata.device_type.lower() == "nine-axis":
            df = pd.DataFrame(self.raw_data[:,0:9], columns=["x_accel_hr", "y_accel_hr", "z_accel_hr",
                                                      "x_gyro", "y_gyro", "z_gyro",
                                                      "pulse", "ambient", "temperature"])
        else:
            raise ValueError("Device type '{}' not recognized.".format(self.metadata.device_type))

        return df


class DASHRData:
    device_type: str
    fileset: list[DASHRDataFile]
    metadata: DASHRMetadata
    x_acceleration: np.ndarray
    y_acceleration: np.ndarray
    z_acceleration: np.ndarray

    x_acceleration_low_range: np.ndarray
    y_acceleration_low_range: np.ndarray
    z_acceleration_low_range: np.ndarray

    x_gyro: np.ndarray
    y_gyro: np.ndarray
    z_gyro: np.ndarray
    temperature: np.ndarray
    light: np.ndarray
    pulse: np.ndarray

    time: np.ndarray

    dataframe: pd.DataFrame

    def __init__(self, data_path:str=None):
        if data_path is None:
            self.device_type = "Not Set"
            self.fileset = []
        else:
            if not os.path.exists(data_path):
                raise FileNotFoundError(data_path)

            if os.path.isdir(data_path):
                # Load data as folder
                dashr_data_files = self.read_folder(data_path)

                if not all(file.metadata.device_type == dashr_data_files[0].metadata.device_type for file in dashr_data_files):
                    self.device_type = "mixed"
                    raise Warning("Not all files loaded are the same device type.")
                else:
                    self.device_type = dashr_data_files[0].metadata.device_type

                self.fileset = dashr_data_files

            elif os.path.isfile(data_path):
                # Load data as a single file
                self.fileset = [self.read_bin(data_path)]
                self.device_type = self.fileset[0].metadata.device_type
            else:
                raise FileNotFoundError(data_path)

            trigger_times = [x.metadata.trigger_time for x in self.fileset]

            if len(trigger_times) > 1:
                if not all(x < y for x, y in zip(trigger_times, trigger_times[1:])):
                    raise Warning("Trigger times appear to be out of order. Your data may have issues.")

            self.metadata = self.fileset[0].metadata
            self.dataframe = self.to_dataframe()
            self.update_measurements()

    def __old__init__(self, device_type: str, fileset: list[DASHRDataFile]):
        self.device_type = device_type
        self.fileset = fileset
        trigger_times = [x.metadata.trigger_time for x in self.fileset]
        if not all(x < y for x, y in zip(trigger_times, trigger_times[1:])):
            raise Warning("Trigger times appear to be out of order. Your data may have issues.")

        self.metadata = fileset[0].metadata
        self.dataframe = self.to_dataframe()
        self.update_measurements()

    def __str__(self):
        return f"{self.device_type} data object with {len(self.fileset)} files and {len(self.dataframe)} data points."


    def read_folder(self, folder_path:str) -> list[DASHRDataFile]:
        """Loads all data from a folder (and subfolders) and converts to a DASHRData object.

        :param folder_path: Folder path to raw .bin data
        :return: Converted DASHRData object
        :rtype: DASHRData
        """
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(folder_path)

        list_of_bins = natsorted(glob.glob(f"{folder_path}/**/*.BIN", recursive=True))
        dashr_data_files = [self.read_bin(x) for x in tqdm(list_of_bins)]
        return dashr_data_files


    def read_bin(self, filename:str) -> DASHRDataFile:
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
            file_metadata = self.__process_header(header_data)
            file_data = []  # np.empty((0,file_metadata.num_digital_channels), dtype=float)
            while f.tell() != end_position:
                current_data_segment = f.read(512)
                if len(current_data_segment) != 0:
                    current_block = self.__process_block(current_data_segment, file_metadata)
                    file_data.append(current_block)  # np.append(file_data, current_block)
            # file_data.reshape(file_data.shape[0]//file_metadata.num_digital_channels, file_metadata.num_digital_channels)
            file_data = np.concatenate(file_data)
        return DASHRDataFile(file_metadata, file_data)


    @staticmethod
    def __process_block(current_data_segment: bytes, file_metadata: DASHRMetadata) -> np.ndarray:
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

        # The rest of the data line is processed here.
        data_end = divmod(500, file_metadata.pin_count * 2)[1]
        data_chunk = struct.unpack(f"{int((500 - data_end) / 2)}H", current_data_segment[12:-data_end])
        data_chunk = np.array(data_chunk, dtype='float').reshape(file_metadata.timesteps_per_block,
                                                                 file_metadata.num_digital_channels)
        # Convert acceleration values
        if file_metadata.num_digital_channels == 9:
            data_chunk = DASHRData.nine_channel_read_line(data_chunk)
        elif file_metadata.num_digital_channels == 12:
            data_chunk = DASHRData.twelve_channel_read_line(data_chunk)
        else:
            raise ValueError(f"Unsupported number of sensor channels: {file_metadata.num_digital_channels}")

        # Append the metadata from this current data chunk (for internal use)
        data_block_count = np.full((data_chunk.shape[0], 1), chunk_header[0])
        write_flag = np.full((data_chunk.shape[0], 1), chunk_header[1])
        start_trigger_flag = np.full((data_chunk.shape[0], 1), chunk_header[2])
        stop_trigger_flag = np.full((data_chunk.shape[0], 1), chunk_header[3])
        trigger_count = np.full((data_chunk.shape[0], 1), chunk_header[4])

        # Per the DynamicDataLogger git repository, this is the millisecond time of the LAST timestep in the block.
        millis_time = np.full((data_chunk.shape[0], 1), chunk_header[5])

        data_chunk = np.hstack(
            (data_chunk, data_block_count, write_flag, start_trigger_flag, stop_trigger_flag, trigger_count, millis_time))

        return data_chunk

    @staticmethod
    def convert_raw_temp(raw_value: np.ndarray, room_temp_offset: float = 25.0,
                         temp_sensitivity: float = 326.8) -> np.ndarray:
        value = (raw_value / temp_sensitivity) + room_temp_offset
        return value

    @staticmethod
    def convert_raw_value(raw_value: np.ndarray, full_scale_range: int) -> np.ndarray:
        value = (raw_value - 32768.0) * (full_scale_range / 32768.0)
        return value

    @staticmethod
    def nine_channel_read_line(data: np.array) -> np.array:
        """Processes data from a single chunk of DASHR 9-axis data"""
        # Convert Acceleration Data
        data[:, 0:3] = DASHRData.convert_raw_value(data[:, 0:3], 200)
        # Convert Gyroscope Data
        data[:, 3:6] = DASHRData.convert_raw_value(data[:, 3:6], 4000)
        # Pass through pulse/temperature
        data[:, 6:8] = data[:, 6:8]
        # Convert Temperature data (from ITG-3701)
        data[:, 8] = DASHRData.convert_raw_temp(data[:, 8], 21, 321.4)

        return data

    @staticmethod
    def twelve_channel_read_line(data: np.ndarray) -> np.ndarray:
        """Processes data from a single chunk of DASHR 12-axis data"""
        # Convert Acceleration Data (High Range)
        data[:, 0:3] = DASHRData.convert_raw_value(data[:, 0:3], 200)
        # Convert Acceleration Data (Low Range)
        data[:, 3:6] = DASHRData.convert_raw_value(data[:, 3:6], 32)
        # Convert Gyroscope Data
        data[:, 6:9] = DASHRData.convert_raw_value(data[:, 6:9], 4000)
        # Pass through pulse
        data[:, 9:11] = data[:, 9:11]
        # Convert Temperature data (from ICM-20601)
        data[:, 11] = DASHRData.convert_raw_temp(data[:, 11], 25, 326.8)

        return data

    @staticmethod
    def __process_header(header: bytes) -> DASHRMetadata:
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

    def update_measurements(self):
        self.x_acceleration = self.dataframe.x_accel_hr
        self.y_acceleration = self.dataframe.y_accel_hr
        self.z_acceleration = self.dataframe.z_accel_hr
        if self.device_type == "twelve-axis":
            self.x_acceleration_low_range = self.dataframe.x_accel_lr
            self.y_acceleration_low_range = self.dataframe.y_accel_lr
            self.z_acceleration_low_range = self.dataframe.z_accel_lr
        self.x_gyro = self.dataframe.x_gyro
        self.y_gyro = self.dataframe.y_gyro
        self.z_gyro = self.dataframe.z_gyro
        self.temperature = self.dataframe.temperature
        self.ambient = self.dataframe.ambient
        self.pulse = self.dataframe.pulse
        self.dataframe = self.dataframe.assign(time=self.dataframe.index / self.metadata.sample_frequency)
        self.time = self.dataframe.time

    def add_data(self, new_data: DASHRDataFile | str):
        """Add new data to the internal fileset and dataframe representation.

        :param new_data: additional `DASHRDataFile` data that will be added to the internal fileset.
        """
        if not isinstance(new_data, DASHRDataFile):
            if os.path.exists(new_data) and os.path.isdir(new_data):
                data = self.read_folder(new_data)
                self.fileset.extend(data)
            elif os.path.exists(new_data) and os.path.isfile(new_data):
                data = self.read_bin(new_data)
                self.fileset.append(data)
            else:
                raise FileNotFoundError("Data file(s) not found.")

        self.dataframe = pd.concat([self.dataframe, new_data.to_dataframe()], ignore_index=True)
        self.update_measurements()


    def to_dataframe(self) -> pd.DataFrame:
        """Concatenate all `DASHRDataFile`s in the fileset to a single DataFrame."""
        df = pd.concat([x.to_dataframe() for x in self.fileset], ignore_index=True, axis=0)
        df = df.assign(time=df.index / self.metadata.sample_frequency)
        col_list = df.columns[:-1].to_list()
        col_list.insert(0, 'time')
        return df[col_list]

    def save_as_csv(self, output_filename: str):
        self.update_measurements()
        self.dataframe.to_csv(output_filename, index=False)
