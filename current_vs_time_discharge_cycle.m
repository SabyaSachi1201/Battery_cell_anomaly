% Specify the folder containing the CSV files
folderPath = 'Data_chunk';

% Get a list of all files in the folder
allFiles = dir(fullfile(folderPath, '*.csv'));

% Initialize a flag to track if it's the first plot
firstPlot = true;
timeOffset = 0; % Initialize time offset

% Create a new figure for the combined plot
figure;
hold on; % Enable holding of subsequent plots

% Loop through each file
for i = 1:length(allFiles)
    currentFile = allFiles(i).name;
    filePath = fullfile(folderPath, currentFile);

    try
        % Read the CSV file into a table
        dataTable = readtable(filePath);

        % Check if the table contains the required variables
        if ismember('Voltage_load', dataTable.Properties.VariableNames) && ...
           ismember('Current_load', dataTable.Properties.VariableNames) && ...
           ismember('Current_measured', dataTable.Properties.VariableNames)

            % Assuming the first column represents time (you might need to adjust this)
            if size(dataTable, 2) > 1
                timeData = dataTable{:, 6}; % Assuming the first column is time
                currentData = dataTable.Current_measured;

                % Shift the time data for subsequent plots
                if ~firstPlot
                    timeData = timeData + timeOffset;
                end

                % Plot the data
                plot(timeData, currentData);

                % Update the time offset for the next plot
                if ~isempty(timeData)
                    timeOffset = timeData(end);
                end

                % Set the flag to false after the first plot
                firstPlot = false;
            else
                warning(['File "', currentFile, '" has insufficient columns for time data. Skipping.']);
            end

        else
            disp(['Skipping file "', currentFile, '" as it does not contain "Voltage_load", "Current_load", and "Current_measured".']);
        end

    catch ME
        warning(['Error reading or processing file "', currentFile, '": ', ME.message]);
    end
end

% Add labels and title to the combined plot
xlabel('Time');
ylabel('Current Measured');
title('Combined Current vs. Time from Multiple Files');
grid on;
hold off; % Release the hold