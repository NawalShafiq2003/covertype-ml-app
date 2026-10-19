export type Option = { value: string; label: string };

export type Feature = {
  name: string;
  label: string;
  kind: 'number' | 'category';
  required: boolean;
  options?: Option[];
  min?: number;
  max?: number;
};

// Raw input fields of the Covertype pipeline (12 fields). The Flask API derives the
// engineered features and applies the saved scaling, so users type REAL units.
export const FEATURES: Feature[] = [
  { name: 'Elevation', label: 'Elevation (m)', kind: 'number', required: true, min: 1859, max: 3858 },
  { name: 'Aspect', label: 'Aspect (degrees azimuth)', kind: 'number', required: true, min: 0, max: 359 },
  { name: 'Slope', label: 'Slope (degrees)', kind: 'number', required: true, min: 0, max: 66 },
  { name: 'Horizontal_Distance_To_Hydrology', label: 'Horizontal distance to water (m)', kind: 'number', required: true, min: 0, max: 1397 },
  { name: 'Vertical_Distance_To_Hydrology', label: 'Vertical distance to water (m)', kind: 'number', required: true, min: -173, max: 601 },
  { name: 'Horizontal_Distance_To_Roadways', label: 'Horizontal distance to roadway (m)', kind: 'number', required: true, min: 0, max: 7117 },
  { name: 'Hillshade_9am', label: 'Hillshade 9am (0-255)', kind: 'number', required: true, min: 0, max: 255 },
  { name: 'Hillshade_Noon', label: 'Hillshade noon (0-255)', kind: 'number', required: true, min: 0, max: 255 },
  { name: 'Hillshade_3pm', label: 'Hillshade 3pm (0-255)', kind: 'number', required: true, min: 0, max: 255 },
  { name: 'Horizontal_Distance_To_Fire_Points', label: 'Horizontal distance to fire point (m)', kind: 'number', required: true, min: 0, max: 7173 },
  { name: 'Wilderness_Area', label: 'Wilderness area', kind: 'category', required: true,
    options: [{ value: '1', label: '1 - Rawah' }, { value: '2', label: '2 - Neota' }, { value: '3', label: '3 - Comanche Peak' }, { value: '4', label: '4 - Cache la Poudre' }] },
  { name: 'Soil_Type', label: 'Soil type', kind: 'category', required: true,
    options: [{ value: '1', label: 'Soil type 1' }, { value: '2', label: 'Soil type 2' }, { value: '3', label: 'Soil type 3' }, { value: '4', label: 'Soil type 4' }, { value: '5', label: 'Soil type 5' }, { value: '6', label: 'Soil type 6' }, { value: '9', label: 'Soil type 9' }, { value: '10', label: 'Soil type 10' }, { value: '11', label: 'Soil type 11' }, { value: '12', label: 'Soil type 12' }, { value: '13', label: 'Soil type 13' }, { value: '14', label: 'Soil type 14' }, { value: '16', label: 'Soil type 16' }, { value: '17', label: 'Soil type 17' }, { value: '18', label: 'Soil type 18' }, { value: '19', label: 'Soil type 19' }, { value: '20', label: 'Soil type 20' }, { value: '21', label: 'Soil type 21' }, { value: '22', label: 'Soil type 22' }, { value: '23', label: 'Soil type 23' }, { value: '24', label: 'Soil type 24' }, { value: '25', label: 'Soil type 25' }, { value: '26', label: 'Soil type 26' }, { value: '27', label: 'Soil type 27' }, { value: '28', label: 'Soil type 28' }, { value: '29', label: 'Soil type 29' }, { value: '30', label: 'Soil type 30' }, { value: '31', label: 'Soil type 31' }, { value: '32', label: 'Soil type 32' }, { value: '33', label: 'Soil type 33' }, { value: '34', label: 'Soil type 34' }, { value: '35', label: 'Soil type 35' }, { value: '37', label: 'Soil type 37' }, { value: '38', label: 'Soil type 38' }, { value: '39', label: 'Soil type 39' }, { value: '40', label: 'Soil type 40' }] },
];
