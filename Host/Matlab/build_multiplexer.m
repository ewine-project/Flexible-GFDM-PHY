function [mod_mux, demod_mux] = build_multiplexer(M)
    %matrix = (ones(16)) * 16;
    %pattern = matrix;   
    %pattern2 = (ones(M)) * M; 
    %for i = 1:M
    %    pattern(1:M,i) = circshift(1:M, [1 -(i-1)] );
    %    pattern2(1:M,i) = circshift(1:M, [1 (i-1)] );
    %end  
    %pattern2 = fliplr(fliplr(pattern2)');
    %matrix(1:M, 1:M) = pattern2';
    %pattern2 = matrix;
    demod_mux = (ones(16)) * 16;  
    mod_mux = (ones(16)) * 16; 
    for i = 1:M
        demod_mux(1:M,i) = circshift(1:M, [1 -(i-1)] );
        mod_mux(1:M,i) = circshift(1:M, [1 (i-1)] );
    end  
end