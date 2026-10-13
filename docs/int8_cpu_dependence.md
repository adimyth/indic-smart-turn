# int8 results depend on the CPU architecture

The same ONNX files were scored on the same test clips on two machines: an x86 cloud server (AMD EPYC 7543) and a MacBook (Apple M4 Pro, Arm). Four languages, test split, one evaluator.

| Language | Model | Server (x86) | MacBook (Arm) | Difference |
|---|---|---:|---:|---:|
| Kannada | Smart Turn v3.2 fp32 | 56.6 / 0.795 | 56.6 / 0.795 | 0 |
| Kannada | Indic tiny fp32 | 82.3 / 0.876 | 82.3 / 0.876 | 0 |
| Kannada | Smart Turn v3.2 int8 (static) | 77.7 / 0.770 | 74.0 / 0.783 | -3.7 |
| Kannada | Indic tiny int8 (static) | 82.9 / 0.878 | 84.2 / 0.895 | +1.3 |
| Malayalam | Smart Turn v3.2 int8 (static) | 66.9 / 0.657 | 63.8 / 0.664 | -3.1 |
| Malayalam | Indic tiny int8 (static) | 80.9 / 0.823 | 79.4 / 0.830 | -1.5 |
| Telugu | Smart Turn v3.2 int8 (static) | 73.4 / 0.750 | 70.9 / 0.766 | -2.5 |
| Telugu | Indic tiny int8 (static) | 85.1 / 0.898 | 87.9 / 0.900 | +2.8 |
| Assamese | Smart Turn v3.2 int8 (static) | 67.8 / 0.696 | 64.9 / 0.691 | -2.9 |
| Assamese | Indic tiny int8 (static) | 80.4 / 0.837 | 81.5 / 0.850 | +1.1 |

Every fp32 model gives identical accuracy and AUC on both machines, so the audio decoding and feature extraction are identical. Only the int8 files move. ONNX Runtime uses different int8 kernels on x86 and Arm, with different rounding and saturation, so a quantised model is not the same function on the two architectures. Statically quantised files move by up to 3.7 points on a single language. Over the whole 20,431-clip public test, Smart Turn v3.2 int8 scores 81.7 / 0.894 on the server and 81.9 / 0.902 on the MacBook.

What this means for reading the results:

- Compare int8 numbers only when both models were scored on the same machine. Every int8 chart in the README pairs models scored on one machine.
- fp32 numbers can be compared across machines. int8 numbers can differ by about 3 points per language and 1 point overall.
- On Apple Silicon use the fp32 files: they are faster there, and their results do not depend on the CPU.

Raw run for the MacBook side: `python -m indic_turn.eval` on `data/built/{kan,mal,tel,asm}.parquet`, split test.
