function [file_string] = write_ini_file(filename, ini_struct)

    if (~exist('filename', 'var'))
        filename = '';        
    end
    
    if (~exist('ini_struct', 'var'))
        error('No data to be saved!')     
    end    

    if isempty(filename)
        [filename, pathname] = uiputfile('*.ini', 'Select a ini file');
        if isequal(filename,0)
           error('User selected Cancel!')           
        else
           disp(['User selected ', fullfile(pathname, filename)])
           filename = fullfile(pathname, filename);
        end        
    end
    
    %This string is then written into the file
    file_string = {};
    
    if (exist(filename, 'file'))        
        %% Update existing file

        fid = fopen(filename);
        cnt = 0;        
        while (1)

            tline = fgetl(fid);
            cnt = cnt + 1;

            if (~ischar(tline))
                %End of file
                break;
            end

            if (strfind(tline, '#'))
                file_string = {file_string{:} tline};
                %skip line because of a comment                
                continue;
            end

            if (~strfind(tline, '='))
                file_string = {file_string{:} tline};
                %skip line because there is nothing to read
                continue;
            end                     

            %Remove whitespace
            tline = strrep(tline, ' ', '');

            %Split line in variable and value
            strings = strtrim(strsplit(tline,'='));

            %this variable exist in our struct?
            if isfield(ini_struct, strings{1})                
                value = ini_struct.(strings{1});
                tline = [strings{1} '=' value_to_string(value)];
            end
            file_string = {file_string{:} tline};
        end
        fclose(fid);    
        
    else
        %% Create a new file
        fields = fieldnames(ini_struct);
        for line = 1:numel(fields)
            value = ini_struct.(fields{line});
            file_string = {file_string{:} [fields{line} '=' value_to_string(value)]};
        end
        
    end
    %% (Over-)write string into file
    fileID = fopen(filename, 'w');
    [zeilen, spalten] = size(file_string);
    for i = 1:spalten
        fprintf(fileID,'%s\r\n', file_string{i});
    end
    fclose(fileID);
end

function str = value_to_string(value)
    [zeilen,spalten] = size(value);
    str = [];
    if isnumeric(value)
        for i = 1:numel(value)
            str = [str num2str(value(i))];
            if i ~= numel(value)
                str = [str ';'];
            end
        end
    elseif iscellstr(value)
        for i = 1:length(value)
            str = [str value{i}];
            if i ~= numel(value)
                str = [str ';'];
            end            
        end
    else
        str = value;
    end
end