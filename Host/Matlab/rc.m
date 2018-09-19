function [ filter_coeff, idx ] = rc( a, number_of_samples_per_period, number_of_periods, domain, normalize )
% 
% This function returns the coefficients of a root-raised cosine filter.
% 
% 
% function [ g t type ] = rc( a, nsamples, nperiods, domain )
% 
% a             roll-off factor
% nperiods      number of periods
% nsamples      number of samples per period, must be even number
% domain        'time' or 'freq'
% 
% 
% cf. Proakis 4th edition, p. 546
% 

if nargin < 4
    domain = 'time';
    normalize = true;
end

if nargin < 5
    normalize = true;
end


number_of_samples_per_period = double(number_of_samples_per_period);
number_of_periods = double(number_of_periods);
a = double(a);

idx=double([]);
filter_coeff=double([]);
switch domain
case 'time'
        
    %idx = linspace( -number_of_periods/2, number_of_periods/2, number_of_samples_per_period*number_of_periods+1 );
    idx = double(1/number_of_samples_per_period*((1:number_of_samples_per_period*number_of_periods+1)-number_of_samples_per_period*number_of_periods/2-1));
    idx = idx( 1:end-1 );

    filter_coeff = sin(double(pi*idx)) ./ (pi*idx) .* cos(double(pi*a*idx)) ./ ( 1-(2*a*idx).^2 );
    filter_coeff( idx==0 ) = 1;
    filter_coeff( abs(idx)==1/(2*a) ) = sin( pi/(2*a) ) / (pi/(2*a)) * pi/4;

case 'freq'
        
    %idx = linspace( -number_of_samples_per_period/2, number_of_samples_per_period/2, number_of_samples_per_period*number_of_periods+1 );
    idx = double(1/number_of_periods*((1:number_of_samples_per_period*number_of_periods+1)-number_of_samples_per_period*number_of_periods/2-1));
    idx = idx( 1:end-1 );

    filter_coeff = 1/2*(1+cos(double(pi/a*(abs(idx)-(1-a)/2))));
    filter_coeff( (abs(idx)<=(1-a)/2 & abs(idx)>=0 ) ) = 1;
    filter_coeff( abs(idx)>(1+a)/2 ) = 0;
    filter_coeff = ifft(filter_coeff);

otherwise
        
    error( 'filter domain must be either ''time'' or ''freq''' );
        
end

if normalize
    filter_coeff = 1/sqrt( sum( filter_coeff.^2 ) ) * filter_coeff;
end

filter_coeff = reshape(filter_coeff, [ numel(filter_coeff), 1 ] );

end
