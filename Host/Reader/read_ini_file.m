function [ini_struct] = read_ini_file(filename)

    ini_struct = struct();

    if (~exist('filename', 'var'))
        filename = '';        
    end

    if isempty(filename)
        [filename, pathname] = uigetfile('*.ini', 'Select a ini file');
        if isequal(filename,0)
           error('User selected Cancel!')           
        else
           disp(['User selected ', fullfile(pathname, filename)])
           filename = fullfile(pathname, filename);
        end        
    end

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
            %skip line because of a comment
            continue;
        end
        
        if (~strfind(tline, '='))
            %skip line because there is nothing to read
            continue;
        end                     
        
        %Remove whitespace
        tline = strrep(tline, ' ', '');
        
        %Split line in variable and value
        strings = strtrim(strsplit(tline,'='));
        
        if length(strings) ~=  2
            %something is wrong with the line
            disp(['Something is missing in line ' num2str(cnt) ': ' tline]);  
            continue;            
        end
                        
        %Split if array is present
        values = strtrim(strsplit(strings{2},';'));        
        
        %Is the first character a string?
        if (isstrprop(values{1,1}, 'alpha'))
            [zeilen, spalten] = size(values);
            if (spalten > 1)
                ini_struct.(strings{1}) = values;
            else
                ini_struct.(strings{1}) = values{1};
            end
        else                        
            ini_struct.(strings{1}) = string_to_number(values);           
        end
        
    end

    fclose(fid);

end

function number = string_to_number(str)

    number = [];
    
    [zeilen, spalten] = size(str);

    for i = 1:spalten
        
        value = strtrim(str{:,i});
        %Convert complex number in a similar writing style
        value = strrep(value, 'I', 'i');
        value = strrep(value, 'J', 'j');
        %+i5 doesnt work it has to be +i*5
        value = strrep(value, '+i*', '+i');
        value = strrep(value, '+i', '+i*');
        
        number = [number str2double(value)];

    end

end