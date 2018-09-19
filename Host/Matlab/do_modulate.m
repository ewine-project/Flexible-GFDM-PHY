function x = do_modulate(K, M, N, a, D)
    % Modulate the GFDM data matrix with the GFDM system
    %
    % Uses efficient FFT implementation.
    % \param D KxM-matrix containing the data to be transmitted at each
    %          subcarrier and symbol.

    L = K;

    block = D.';

    g = rc( a, K, M, 'time', false );
    g2 = g(1:K/L:end); G2 = fft(g2);
    DD = repmat(fft(block, [], 1), L, 1);

    X = zeros(N,1);

    for k=1:K
        carrier = zeros(N,1);
        carrier(1:L*M) = fftshift(DD(:,k) .* G2);

        carrier = circshift(carrier, -L*M/2 + M*(k-1));
        X = X + carrier;
    end

    X = (K/L) * X;
    x = ifft(X);
end