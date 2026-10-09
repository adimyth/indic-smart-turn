ben: 2116 scored test clips
eng: 2486 scored test clips
guj: 2006 scored test clips
hin: 2165 scored test clips
kan: 367 scored test clips
mal: 462 scored test clips
mar: 925 scored test clips
ori: 95 scored test clips
tam: 991 scored test clips
tel: 1097 scored test clips

### Label = Gemini audio verdict (same labeler as the IndicVoices test set)

| language | n | complete% | model | accuracy | AUC | recall(complete) | recall(incomplete) |
|---|---:|---:|---|---:|---:|---:|---:|
| Bengali | 2116 | 43 | Smart Turn v3.2 int8 | 64.7 | 0.769 | 92.0 | 44.0 |
| Bengali | 2116 | 43 | Indic base fp32 | 77.0 | 0.859 | 88.3 | 68.5 |
| Bengali | 2116 | 43 | Indic base int8 | 77.5 | 0.859 | 88.6 | 69.1 |
| Bengali | 2116 | 43 | Indic tiny int8 | 70.3 | 0.814 | 86.9 | 57.8 |
| English | 2486 | 42 | Smart Turn v3.2 int8 | 67.6 | 0.752 | 71.7 | 64.6 |
| English | 2486 | 42 | Indic base fp32 | 75.4 | 0.830 | 76.1 | 74.9 |
| English | 2486 | 42 | Indic base int8 | 75.2 | 0.829 | 75.8 | 74.8 |
| English | 2486 | 42 | Indic tiny int8 | 71.2 | 0.794 | 77.3 | 66.8 |
| Gujarati | 2006 | 45 | Smart Turn v3.2 int8 | 68.6 | 0.770 | 82.2 | 57.6 |
| Gujarati | 2006 | 45 | Indic base fp32 | 76.4 | 0.858 | 81.2 | 72.6 |
| Gujarati | 2006 | 45 | Indic base int8 | 76.5 | 0.857 | 81.6 | 72.4 |
| Gujarati | 2006 | 45 | Indic tiny int8 | 76.2 | 0.840 | 84.5 | 69.5 |
| Hindi | 2165 | 44 | Smart Turn v3.2 int8 | 68.9 | 0.797 | 87.0 | 54.7 |
| Hindi | 2165 | 44 | Indic base fp32 | 79.0 | 0.875 | 89.5 | 70.7 |
| Hindi | 2165 | 44 | Indic base int8 | 78.8 | 0.876 | 89.7 | 70.1 |
| Hindi | 2165 | 44 | Indic tiny int8 | 75.0 | 0.837 | 87.5 | 65.2 |
| Kannada | 367 | 41 | Smart Turn v3.2 int8 | 64.3 | 0.778 | 89.3 | 47.2 |
| Kannada | 367 | 41 | Indic base fp32 | 73.0 | 0.865 | 89.3 | 61.9 |
| Kannada | 367 | 41 | Indic base int8 | 74.1 | 0.864 | 90.6 | 62.8 |
| Kannada | 367 | 41 | Indic tiny int8 | 67.8 | 0.819 | 88.6 | 53.7 |
| Malayalam | 462 | 52 | Smart Turn v3.2 int8 | 64.1 | 0.732 | 83.4 | 43.0 |
| Malayalam | 462 | 52 | Indic base fp32 | 77.9 | 0.865 | 90.9 | 63.8 |
| Malayalam | 462 | 52 | Indic base int8 | 78.4 | 0.862 | 91.7 | 63.8 |
| Malayalam | 462 | 52 | Indic tiny int8 | 75.8 | 0.819 | 89.2 | 61.1 |
| Marathi | 925 | 47 | Smart Turn v3.2 int8 | 66.4 | 0.780 | 87.5 | 48.0 |
| Marathi | 925 | 47 | Indic base fp32 | 76.9 | 0.856 | 82.8 | 71.7 |
| Marathi | 925 | 47 | Indic base int8 | 77.0 | 0.854 | 84.0 | 70.9 |
| Marathi | 925 | 47 | Indic tiny int8 | 73.4 | 0.820 | 81.7 | 66.2 |
| Odia | 95 | 33 | Smart Turn v3.2 int8 | 70.5 | 0.810 | 87.1 | 62.5 |
| Odia | 95 | 33 | Indic base fp32 | 81.1 | 0.914 | 93.5 | 75.0 |
| Odia | 95 | 33 | Indic base int8 | 78.9 | 0.912 | 93.5 | 71.9 |
| Odia | 95 | 33 | Indic tiny int8 | 66.3 | 0.860 | 90.3 | 54.7 |
| Tamil | 991 | 43 | Smart Turn v3.2 int8 | 61.9 | 0.755 | 90.4 | 40.5 |
| Tamil | 991 | 43 | Indic base fp32 | 79.5 | 0.876 | 92.9 | 69.4 |
| Tamil | 991 | 43 | Indic base int8 | 78.7 | 0.875 | 92.5 | 68.4 |
| Tamil | 991 | 43 | Indic tiny int8 | 70.5 | 0.819 | 86.6 | 58.5 |
| Telugu | 1097 | 41 | Smart Turn v3.2 int8 | 66.2 | 0.788 | 88.8 | 50.5 |
| Telugu | 1097 | 41 | Indic base fp32 | 77.0 | 0.888 | 91.7 | 66.9 |
| Telugu | 1097 | 41 | Indic base int8 | 77.3 | 0.886 | 93.1 | 66.4 |
| Telugu | 1097 | 41 | Indic tiny int8 | 71.8 | 0.825 | 87.1 | 61.3 |

Weighted overall:
  Smart Turn v3.2 int8   accuracy 66.6  AUC 0.771  recall(complete) 84.5  recall(incomplete) 52.8
  Indic base fp32        accuracy 77.1  AUC 0.860  recall(complete) 85.4  recall(incomplete) 70.6
  Indic base int8        accuracy 77.1  AUC 0.859  recall(complete) 85.7  recall(incomplete) 70.4
  Indic tiny int8        accuracy 72.7  AUC 0.821  recall(complete) 84.5  recall(incomplete) 63.6

### Label = what happened in the recording (agent replied = complete; trainee resumed = incomplete)

| language | n | complete% | model | accuracy | AUC | recall(complete) | recall(incomplete) |
|---|---:|---:|---|---:|---:|---:|---:|
| Bengali | 2116 | 18 | Smart Turn v3.2 int8 | 41.5 | 0.645 | 86.1 | 31.7 |
| Bengali | 2116 | 18 | Indic base fp32 | 53.8 | 0.667 | 77.2 | 48.7 |
| Bengali | 2116 | 18 | Indic base int8 | 53.9 | 0.667 | 77.0 | 48.8 |
| Bengali | 2116 | 18 | Indic tiny int8 | 49.2 | 0.657 | 79.6 | 42.5 |
| English | 2486 | 22 | Smart Turn v3.2 int8 | 57.3 | 0.636 | 68.1 | 54.3 |
| English | 2486 | 22 | Indic base fp32 | 63.9 | 0.722 | 73.5 | 61.1 |
| English | 2486 | 22 | Indic base int8 | 64.2 | 0.720 | 74.1 | 61.4 |
| English | 2486 | 22 | Indic tiny int8 | 59.1 | 0.693 | 74.6 | 54.7 |
| Gujarati | 2006 | 18 | Smart Turn v3.2 int8 | 50.8 | 0.680 | 80.2 | 44.2 |
| Gujarati | 2006 | 18 | Indic base fp32 | 58.9 | 0.713 | 78.6 | 54.5 |
| Gujarati | 2006 | 18 | Indic base int8 | 58.6 | 0.713 | 78.6 | 54.1 |
| Gujarati | 2006 | 18 | Indic tiny int8 | 55.7 | 0.689 | 78.6 | 50.6 |
| Hindi | 2165 | 25 | Smart Turn v3.2 int8 | 52.3 | 0.653 | 81.9 | 42.4 |
| Hindi | 2165 | 25 | Indic base fp32 | 56.7 | 0.670 | 75.1 | 50.6 |
| Hindi | 2165 | 25 | Indic base int8 | 56.6 | 0.668 | 75.6 | 50.2 |
| Hindi | 2165 | 25 | Indic tiny int8 | 54.4 | 0.651 | 74.9 | 47.6 |
| Kannada | 367 | 16 | Smart Turn v3.2 int8 | 43.9 | 0.682 | 85.0 | 35.8 |
| Kannada | 367 | 16 | Indic base fp32 | 53.1 | 0.767 | 86.7 | 46.6 |
| Kannada | 367 | 16 | Indic base int8 | 53.1 | 0.762 | 86.7 | 46.6 |
| Kannada | 367 | 16 | Indic tiny int8 | 47.4 | 0.754 | 83.3 | 40.4 |
| Malayalam | 462 | 29 | Smart Turn v3.2 int8 | 45.7 | 0.597 | 78.4 | 32.3 |
| Malayalam | 462 | 29 | Indic base fp32 | 56.5 | 0.688 | 86.6 | 44.2 |
| Malayalam | 462 | 29 | Indic base int8 | 56.1 | 0.688 | 86.6 | 43.6 |
| Malayalam | 462 | 29 | Indic tiny int8 | 53.9 | 0.646 | 82.8 | 42.1 |
| Marathi | 925 | 20 | Smart Turn v3.2 int8 | 45.1 | 0.652 | 83.9 | 35.3 |
| Marathi | 925 | 20 | Indic base fp32 | 58.2 | 0.709 | 79.6 | 52.8 |
| Marathi | 925 | 20 | Indic base int8 | 57.6 | 0.706 | 80.6 | 51.8 |
| Marathi | 925 | 20 | Indic tiny int8 | 56.0 | 0.708 | 80.1 | 49.9 |
| Odia | 95 | 28 | Smart Turn v3.2 int8 | 45.3 | 0.496 | 48.1 | 44.1 |
| Odia | 95 | 28 | Indic base fp32 | 53.7 | 0.564 | 51.9 | 54.4 |
| Odia | 95 | 28 | Indic base int8 | 53.7 | 0.554 | 55.6 | 52.9 |
| Odia | 95 | 28 | Indic tiny int8 | 43.2 | 0.517 | 55.6 | 38.2 |
| Tamil | 991 | 23 | Smart Turn v3.2 int8 | 43.7 | 0.643 | 85.6 | 31.1 |
| Tamil | 991 | 23 | Indic base fp32 | 57.7 | 0.712 | 82.5 | 50.3 |
| Tamil | 991 | 23 | Indic base int8 | 56.9 | 0.715 | 81.7 | 49.5 |
| Tamil | 991 | 23 | Indic tiny int8 | 53.4 | 0.699 | 80.8 | 45.1 |
| Telugu | 1097 | 17 | Smart Turn v3.2 int8 | 45.6 | 0.652 | 82.1 | 37.9 |
| Telugu | 1097 | 17 | Indic base fp32 | 53.5 | 0.673 | 80.5 | 47.9 |
| Telugu | 1097 | 17 | Indic base int8 | 52.7 | 0.671 | 80.5 | 46.9 |
| Telugu | 1097 | 17 | Indic tiny int8 | 52.7 | 0.689 | 82.1 | 46.5 |

Weighted overall:
  Smart Turn v3.2 int8   accuracy 48.9  AUC 0.649  recall(complete) 79.8  recall(incomplete) 40.9
  Indic base fp32        accuracy 57.8  AUC 0.695  recall(complete) 77.6  recall(incomplete) 52.5
  Indic base int8        accuracy 57.6  AUC 0.695  recall(complete) 77.8  recall(incomplete) 52.2
  Indic tiny int8        accuracy 54.2  AUC 0.679  recall(complete) 78.1  recall(incomplete) 48.0
