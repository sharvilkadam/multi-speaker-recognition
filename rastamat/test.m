function C = test(samples, sr)
C = melfcc(samples, sr, 'numcep', 39, 'wintime', 0.025, 'hoptime', 0.010, 'maxfreq', 8000);
