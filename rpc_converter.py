import re


class RPCConverter:
    def __init__(self):
        # Unified internal representation of keys
        self.data = {}
        self.key_map_to_internal = {
            "lineOffset": "line_offset",
            "sampOffset": "samp_offset",
            "latOffset": "lat_offset",
            "longOffset": "long_offset",
            "heightOffset": "height_offset",
            "lineScale": "line_scale",
            "sampScale": "samp_scale",
            "latScale": "lat_scale",
            "longScale": "long_scale",
            "heightScale": "height_scale",
            "lineNumCoef": "line_num_coef",
            "lineDenCoef": "line_den_coef",
            "sampNumCoef": "samp_num_coef",
            "sampDenCoef": "samp_den_coef",
            "LINE_OFF": "line_offset",
            "SAMP_OFF": "samp_offset",
            "LAT_OFF": "lat_offset",
            "LONG_OFF": "long_offset",
            "HEIGHT_OFF": "height_offset",
            "LINE_SCALE": "line_scale",
            "SAMP_SCALE": "samp_scale",
            "LAT_SCALE": "lat_scale",
            "LONG_SCALE": "long_scale",
            "HEIGHT_SCALE": "height_scale",
            "LINE_NUM_COEFF": "line_num_coef",
            "LINE_DEN_COEFF": "line_den_coef",
            "SAMP_NUM_COEFF": "samp_num_coef",
            "SAMP_DEN_COEFF": "samp_den_coef"
        }
        self.key_map_from_internal_to_rpc = {
            "line_offset": "LINE_OFF",
            "samp_offset": "SAMP_OFF",
            "lat_offset": "LAT_OFF",
            "long_offset": "LONG_OFF",
            "height_offset": "HEIGHT_OFF",
            "line_scale": "LINE_SCALE",
            "samp_scale": "SAMP_SCALE",
            "lat_scale": "LAT_SCALE",
            "long_scale": "LONG_SCALE",
            "height_scale": "HEIGHT_SCALE",
        }
        self.key_map_from_internal_to_rpb = {
            "line_offset": "lineOffset",
            "samp_offset": "sampOffset",
            "lat_offset": "latOffset",
            "long_offset": "longOffset",
            "height_offset": "heightOffset",
            "line_scale": "lineScale",
            "samp_scale": "sampScale",
            "lat_scale": "latScale",
            "long_scale": "longScale",
            "height_scale": "heightScale",
        }

    def read_rpb(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()

        self.data = {}
        for match in re.finditer(r'(\w+)\s*=\s*([^\n;]+)', content):
            key = match.group(1).strip()
            value = match.group(2).strip().strip(";")
            internal_key = self.key_map_to_internal.get(key)
            if internal_key:
                if key in ['lineNumCoef', 'lineDenCoef', 'sampNumCoef', 'sampDenCoef']:
                    value = [float(x) for x in re.findall(r'[+-]?\d+\.\d+E[+-]\d+', value)]
                else:
                    value = float(value)
                self.data[internal_key] = value

    def read_rpc(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()

        self.data = {
            "line_num_coef": [],
            "line_den_coef": [],
            "samp_num_coef": [],
            "samp_den_coef": []
        }

        for match in re.finditer(r'(\w+)\s*:\s*([^\n]+)', content):
            key = match.group(1).strip()
            value = float(match.group(2).strip().split()[0])

            if "COEFF" in key.upper():
                \54321
                internal_key = key.lower().rsplit('_', 1)[0]
                internal_key = internal_key[:-1]
                self.data[internal_key].append(value)
            else:
                internal_key = self.key_map_to_internal.get(key.upper())
                if internal_key:
                    self.data[internal_key] = value

    def write_rpb(self, file_path):
        with open(file_path, 'w') as file:
            file.write('satId = "XXX";\n')
            file.write('bandId = "XXX";\n')
            file.write('SpecId = "XXX";\n')
            file.write('BEGIN_GROUP = IMAGE\n')
            file.write(f'    errBias =   1.0;\n')
            file.write(f'    errRand =    0.0;\n')

            for internal_key, rpb_key in self.key_map_from_internal_to_rpb.items():
                if internal_key in self.data:
                    file.write(f'    {rpb_key} = {self.data[internal_key]};\n')

            file.write('    lineNumCoef = (\n')
            file.write(',\n'.join(f'        {coef:+.16E}' for coef in self.data["line_num_coef"]))
            file.write(');\n')
            file.write('    lineDenCoef = (\n')
            file.write(',\n'.join(f'        {coef:+.16E}' for coef in self.data["line_den_coef"]))
            file.write(');\n')
            file.write('    sampNumCoef = (\n')
            file.write(',\n'.join(f'        {coef:+.16E}' for coef in self.data["samp_num_coef"]))
            file.write(');\n')
            file.write('    sampDenCoef = (\n')
            file.write(',\n'.join(f'        {coef:+.16E}' for coef in self.data["samp_den_coef"]))
            file.write(');\n')
            file.write('END_GROUP = IMAGE\nEND;\n')

    def write_rpc(self, file_path):
        with open(file_path, 'w') as file:
            for internal_key, rpc_key in self.key_map_from_internal_to_rpc.items():
                if internal_key in self.data:
                    file.write(f"{rpc_key}: {self.data[internal_key]:+013.4f}  {self.get_units(rpc_key)}\n")

            for i, coef in enumerate(self.data['line_num_coef']):
                file.write(f"LINE_NUM_COEFF_{i + 1:02d}: {coef:+.16E}\n")
            for i, coef in enumerate(self.data['line_den_coef']):
                file.write(f"LINE_DEN_COEFF_{i + 1:02d}: {coef:+.16E}\n")
            for i, coef in enumerate(self.data['samp_num_coef']):
                file.write(f"SAMP_NUM_COEFF_{i + 1:02d}: {coef:+.16E}\n")
            for i, coef in enumerate(self.data['samp_den_coef']):
                file.write(f"SAMP_DEN_COEFF_{i + 1:02d}: {coef:+.16E}\n")

    def convert(self, input_file, output_file, output_format):
        if input_file.endswith('.rpb'):
            self.read_rpb(input_file)
        elif input_file.endswith('.rpc'):
            self.read_rpc(input_file)
        else:
            raise ValueError("Unsupported file format")

        if output_format == 'rpb':
            self.write_rpb(output_file)
        elif output_format == 'rpc':
            self.write_rpc(output_file)
        else:
            raise ValueError("Unsupported output format")

    def get_units(self, key):
        units_map = {
            "LINE_OFF": "pixels",
            "SAMP_OFF": "pixels",
            "LAT_OFF": "degrees",
            "LONG_OFF": "degrees",
            "HEIGHT_OFF": "meters",
            "LINE_SCALE": "pixels",
            "SAMP_SCALE": "pixels",
            "LAT_SCALE": "degrees",
            "LONG_SCALE": "degrees",
            "HEIGHT_SCALE": "meters"
        }
        return units_map.get(key, '')


# Example usage:
if __name__ == '__main__':
    converter = RPCConverter()
    # converter.convert("input.rpb", "output.rpc", "rpc")
    converter.convert(r"G:\DataSets\E010\E010B\OrigImage\0575092.rpc", "output.rpb", "rpb")
