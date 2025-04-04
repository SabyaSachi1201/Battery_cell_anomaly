% Specify the folder containing the original CSV files
inputFolderPath = 'Data_chunk';

% Specify the folder to save the new CSV files with SoC
outputFolderPath = 'Data_with_SoC';
if ~exist(outputFolderPath, 'dir')
    mkdir(outputFolderPath);
end

% Battery Nominal Capacity (in Ampere-hours - Ah) - ADJUST THIS VALUE
batteryCapacityAh = 2.0; % Example: 2.0 Ah
batteryCapacityC = batteryCapacityAh * 3600; % Convert to Coulombs

% Initial SoC (as a fraction, e.g., 1 for 100%) - ADJUST THIS VALUE
initialSoC = 1.0;

% Get a list of all files in the input folder
allFiles = dir(fullfile(inputFolderPath, '*.csv'));

% Loop through each file
for i = 1:length(allFiles)
    currentFileName = allFiles(i).name;
    inputFilePath = fullfile(inputFolderPath, currentFileName);
    [~, name, ext] = fileparts(currentFileName);
    outputFileName = [name, '_with_SoC', ext];
    outputFilePath = fullfile(outputFolderPath, outputFileName);

    try
        % Read the CSV file into a table
        dataTable = readtable(inputFilePath);

        % Check if the table contains the necessary variables
        if ismember({'Voltage_measured', 'Current_measured', 'Temperature_measured', ...
                     'Current_load', 'Voltage_load'}, dataTable.Properties.VariableNames)

            % Initialize SoC array
            numRows = height(dataTable);
            estimatedSoC = zeros(numRows, 1);
            estimatedSoC(1) = initialSoC; % Set initial SoC for the first point

            % Determine the time data source
            if ismember('Time', dataTable.Properties.VariableNames)
                timeData = dataTable.Time;
            elseif size(dataTable, 2) > 1
                timeData = dataTable{:, 1}; % Assuming the first column is time in seconds
            else
                warning(['File "', currentFileName, '" does not have a "Time" column and has only one column. Skipping SoC calculation.']);
                continue;
            end

            % Calculate Estimated SoC using Coulomb Counting (as per your reference)
            for j = 2:numRows
                dt = timeData(j) - timeData(j-1);
                current = dataTable.Current_measured(j);
                estimatedSoC(j) = estimatedSoC(j-1) + (current * dt) / batteryCapacityC;
            end

            % Add the Estimated_SOC column to the table
            dataTable.Estimated_SOC = estimatedSoC;

            % Select the desired columns for the new CSV file
            outputTable = dataTable(:, {'Voltage_measured', 'Current_measured', 'Temperature_measured', ...
                                       'Current_load', 'Voltage_load', 'Estimated_SOC'});

            % Add the 'Time' column to the output table
            if ismember('Time', dataTable.Properties.VariableNames)
                outputTable.Time = dataTable.Time;
            elseif size(dataTable, 2) > 1
                outputTable.Time = timeData;
            end

            % Reorder columns to match the requested order
            outputTable = outputTable(:, {'Voltage_measured', 'Current_measured', 'Temperature_measured', ...
                                       'Current_load', 'Voltage_load', 'Time', 'Estimated_SOC'});

            % Write the new table to a new CSV file
            writetable(outputTable, outputFilePath);
            disp(['Processed and saved SoC for file: ', currentFileName]);

        else
            disp(['Skipping file "', currentFileName, '" as it does not contain all the required variables.']);
        end

    catch ME
        warning(['Error reading or processing file "', currentFileName, '": ', ME.message]);
    end
end

disp('Finished processing all files.');