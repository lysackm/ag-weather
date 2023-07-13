# Random Forest Tree Tuning: Temperature Error

## Summary

max_features = None (include all features) and min_samples_leaf = 1
(number of hits to create a leaf in the random forest) are optimal.
Using the actual temperature as an output gives a better root mean 
squared error.


### n_estimators: 50, max_features: 0.3, min_samples_leaf: 1

Root mean squared error: 2.48

Test data R-2 score: 0.101

Test data Spearman correlation: 0.441

Test data Pearson correlation: 0.441

[0.01751894 0.01438968 0.03277535 0.68477037 0.09017399 0.14370512
 0.01666656]


### n_estimators: 50, max_features: 0.3, min_samples_leaf: 10

Root mean squared error: 2.17

Test data R-2 score: 0.315

Test data Spearman correlation: 0.559

Test data Pearson correlation: 0.562

[0.03713689 0.02925195 0.06586693 0.3994775  0.19538873 0.24340909
 0.02946892]


### n_estimators: 50, max_features: 0.3, min_samples_leaf: 100

Root mean squared error: 2.16

Test data R-2 score:  0.32

Test data Spearman correlation: 0.565

Test data Pearson correlation: 0.567

[0.04538282 0.03181478 0.07761102 0.30069771 0.2398622  0.27626278
 0.02836869]


### n_estimators: 50, max_features: None, min_samples_leaf: 1

Root mean squared error: 2.1

Test data R-2 score: 0.356

Test data Spearman correlation: 0.596

Test data Pearson correlation: 0.604

[0.03637126 0.03322748 0.07418369 0.57884941 0.06962912 0.16176552
 0.04597352]


### n_estimators: 50, max_features: None, min_samples_leaf: 10

Root mean squared error: 2.1

Test data R-2 score: 0.354

Test data Spearman correlation: 0.59

Test data Pearson correlation: 0.595

[0.04614352 0.03434605 0.09046857 0.45578592 0.12002483 0.2171622
 0.03606892]

### n_estimators: 50, max_features: None, min_samples_leaf: 100

Root mean squared error: 2.14

Test data R-2 score: 0.332

Test data Spearman correlation: 0.573

Test data Pearson correlation: 0.576

[0.04913815 0.02951483 0.09847919 0.36539888 0.16752276 0.26994909
 0.01999709]


### n_estimators: 100, max_features: 0.3, min_samples_leaf: 1

Root mean squared error: 2.48

Test data R-2 score: 0.104

Test data Spearman correlation: 0.442

Test data Pearson correlation: 0.442

[0.01717418 0.01450989 0.03260445 0.68624677 0.0909678  0.14148602
 0.0170109 ]


### n_estimators: 100, max_features: 0.3, min_samples_leaf: 10

Root mean squared error: 2.17

Test data R-2 score: 0.316

Test data Spearman correlation: 0.559

Test data Pearson correlation: 0.563

[0.03670697 0.02850073 0.06651658 0.41100673 0.18323736 0.24433235
 0.02969927]


### n_estimators: 100, max_features: 0.3, min_samples_leaf: 100

Root mean squared error: 2.16

Test data R-2 score: 0.321

Test data Spearman correlation: 0.566

Test data Pearson correlation: 0.568

[0.04525997 0.03324125 0.07834324 0.31283795 0.22774366 0.27426894
 0.02830499]


### n_estimators: 100, max_features: None, min_samples_leaf: 1

Root mean squared error: 2.09

Test data R-2 score: 0.362

Test data Spearman correlation: 0.6

Test data Pearson correlation: 0.608

[0.03646879 0.03324991 0.07431586 0.5785577  0.06985212 0.161497
 0.04605862]


### n_estimators: 100, max_features: None, min_samples_leaf: 10

Root mean squared error: 2.1
Test data R-2 score: 0.356

Test data Spearman correlation: 0.591

Test data Pearson correlation: 0.597

[0.04600355 0.03434031 0.09056986 0.4555811  0.11997129 0.21740605
 0.03612784]


### n_estimators: 100, max_features: None, min_samples_leaf: 100

Root mean squared error: 2.14

Test data R-2 score: 0.332

Test data Spearman correlation: 0.574

Test data Pearson correlation: 0.576

[0.0491354  0.0294211  0.09850302 0.36546631 0.1675157  0.27010991
 0.01984856]


### n_estimators: 150, max_features: 0.3, min_samples_leaf: 1

Root mean squared error: 2.47

Test data R-2 score: 0.107

Test data Spearman correlation: 0.443

Test data Pearson correlation: 0.444

[0.01700976 0.01394386 0.03295173 0.68644402 0.09007796 0.14290514
 0.01666752]


### n_estimators: 150, max_features: 0.3, min_samples_leaf: 10

Root mean squared error: 2.16

Test data R-2 score: 0.317

Test data Spearman correlation: 0.56

Test data Pearson correlation: 0.563

[0.03589515 0.0279285  0.06783567 0.40223578 0.19385506 0.24280835
 0.02944149]


### n_estimators: 150, max_features: 0.3, min_samples_leaf: 100

Root mean squared error: 2.16

Test data R-2 score: 0.321

Test data Spearman correlation: 0.566

Test data Pearson correlation: 0.568

[0.04501525 0.03217982 0.07949261 0.29521164 0.24494212 0.27516
 0.02799857]


### n_estimators: 150, max_features: None, min_samples_leaf: 1

Root mean squared error: 2.09

Test data R-2 score: 0.364

Test data Spearman correlation: 0.601

Test data Pearson correlation: 0.609

[0.03652735 0.03328282 0.07431755 0.5785617  0.06969414 0.16160568
 0.04601076]


### n_estimators: 150, max_features: None, min_samples_leaf: 10

Root mean squared error: 2.1

Test data R-2 score: 0.356

Test data Spearman correlation: 0.592

Test data Pearson correlation: 0.597

[0.04615476 0.03437893 0.09060128 0.45571116 0.12001991 0.21696425
 0.03616972]


### n_estimators: 150, max_features: None, min_samples_leaf: 100

Root mean squared error: 2.14

Test data R-2 score: 0.332

Test data Spearman correlation: 0.574

Test data Pearson correlation: 0.576

[0.04934241 0.02939194 0.09838309 0.36535449 0.16762085 0.27007685
 0.01983037]


# Random Forest Tree Tuning: Temperature Error

### n_estimators: 50, max_features: 0.3, min_samples_leaf: 1

Root mean squared error: 2.36

Test data R-2 score: 0.974

Test data Spearman correlation: 0.988

Test data Pearson correlation: 0.987

[0.00095034 0.00088808 0.00163796 0.7036398  0.27084533 0.02106299
 0.00097549]


### n_estimators: 50, max_features: 0.3, min_samples_leaf: 10

Root mean squared error: 2.14

Test data R-2 score: 0.979

Test data Spearman correlation: 0.99

Test data Pearson correlation: 0.989

[8.70089810e-04 6.68562242e-04 1.24935873e-03 7.09334296e-01
 2.69412323e-01 1.78723443e-02 5.93025002e-04]


### n_estimators: 50, max_features: 0.3, min_samples_leaf: 100

Root mean squared error: 2.22

Test data R-2 score: 0.977

Test data Spearman correlation: 0.989

Test data Pearson correlation: 0.989

[7.72429382e-04 4.95450730e-04 9.36742661e-04 6.96528195e-01
 2.82065073e-01 1.89239543e-02 2.78155095e-04]


### n_estimators: 50, max_features: None, min_samples_leaf: 1

Root mean squared error: 1.97

Test data R-2 score: 0.982

Test data Spearman correlation: 0.991

Test data Pearson correlation: 0.991

[0.00162549 0.0015793  0.00322309 0.98263772 0.00284131 0.00593488
 0.00215821]


### n_estimators: 50, max_features: None, min_samples_leaf: 10

Root mean squared error: 2.08

Test data R-2 score:  0.98

Test data Spearman correlation: 0.99

Test data Pearson correlation: 0.99

[9.67281912e-04 7.89398823e-04 1.85195246e-03 9.89247539e-01
 2.28325164e-03 4.05012495e-03 8.10451568e-04]


### n_estimators: 50, max_features: None, min_samples_leaf: 100

Root mean squared error: 2.17

Test data R-2 score: 0.978

Test data Spearman correlation: 0.99

Test data Pearson correlation: 0.989

[5.35548533e-04 2.88194189e-04 1.07240174e-03 9.92925859e-01
 1.91160724e-03 3.12491702e-03 1.41472518e-04]


### n_estimators: 100, max_features: 0.3, min_samples_leaf: 1

Root mean squared error: 2.35

Test data R-2 score: 0.974

Test data Spearman correlation: 0.988

Test data Pearson correlation: 0.987

[0.00103644 0.00086459 0.00162469 0.73116038 0.24250095 0.02185119
 0.00096176]


### n_estimators: 100, max_features: 0.3, min_samples_leaf: 10

Root mean squared error: 2.14

Test data R-2 score: 0.979

Test data Spearman correlation: 0.99

Test data Pearson correlation: 0.989

[8.76927811e-04 6.80338538e-04 1.23666641e-03 7.09709613e-01
 2.68538437e-01 1.83781827e-02 5.79833940e-04]


### n_estimators: 100, max_features: 0.3, min_samples_leaf: 100

Root mean squared error: 2.21

Test data R-2 score: 0.977

Test data Spearman correlation: 0.989

Test data Pearson correlation: 0.989

[7.19315869e-04 4.85272058e-04 9.75547984e-04 6.75436208e-01
 3.04978135e-01 1.71326831e-02 2.72837712e-04]


### n_estimators: 100, max_features: None, min_samples_leaf: 1

Root mean squared error: 1.96

Test data R-2 score: 0.982

Test data Spearman correlation: 0.991

Test data Pearson correlation: 0.991

[0.00162798 0.00157929 0.00322917 0.98263265 0.00283798 0.00593597
 0.00215696]


### n_estimators: 100, max_features: None, min_samples_leaf: 10

Root mean squared error: 2.07

Test data R-2 score:  0.98

Test data Spearman correlation: 0.99

Test data Pearson correlation: 0.99

[9.67099888e-04 7.89069764e-04 1.85162844e-03 9.89242480e-01
 2.28302165e-03 4.05422685e-03 8.12473808e-04]


### n_estimators: 100, max_features: None, min_samples_leaf: 100

Root mean squared error: 2.17

Test data R-2 score: 0.978

Test data Spearman correlation: 0.99

Test data Pearson correlation: 0.989

[5.34066200e-04 2.89627979e-04 1.07509375e-03 9.92922330e-01
 1.91341807e-03 3.12387357e-03 1.41590441e-04]


### n_estimators: 150, max_features: 0.3, min_samples_leaf: 1

Root mean squared error: 2.35

Test data R-2 score: 0.974

Test data Spearman correlation: 0.988

Test data Pearson correlation: 0.987

[0.0010115  0.00085778 0.00160439 0.69844626 0.27572517 0.02141639
 0.00093852]


### n_estimators: 150, max_features: 0.3, min_samples_leaf: 10

Root mean squared error: 2.14

Test data R-2 score: 0.979

Test data Spearman correlation: 0.99

Test data Pearson correlation: 0.989

[8.50241891e-04 6.68061150e-04 1.24437601e-03 7.51626603e-01
 2.26398632e-01 1.86237056e-02 5.88379918e-04]


### n_estimators: 150, max_features: 0.3, min_samples_leaf: 100

Root mean squared error: 2.21

Test data R-2 score: 0.977

Test data Spearman correlation: 0.989

Test data Pearson correlation: 0.989

[7.30486040e-04 4.89514173e-04 9.64657668e-04 6.78076013e-01
 3.01438358e-01 1.80236547e-02 2.77316306e-04]


### n_estimators: 150, max_features: None, min_samples_leaf: 1

Root mean squared error: 1.96

Test data R-2 score: 0.982

Test data Spearman correlation: 0.991

Test data Pearson correlation: 0.991

[0.00162697 0.00157914 0.003228   0.98263524 0.00283782 0.005935
 0.00215782]

### n_estimators: 150, max_features: None, min_samples_leaf: 10

Root mean squared error: 2.07

Test data R-2 score:  0.98

Test data Spearman correlation: 0.99

Test data Pearson correlation: 0.99

[9.68421570e-04 7.89128395e-04 1.85099823e-03 9.89245276e-01
 2.28108438e-03 4.05511422e-03 8.09976963e-04]


### n_estimators: 150, max_features: None, min_samples_leaf: 100

Root mean squared error: 2.17

Test data R-2 score: 0.978

Test data Spearman correlation: 0.99

Test data Pearson correlation: 0.989

[5.34745407e-04 2.89741414e-04 1.07390408e-03 9.92924257e-01
 1.91260451e-03 3.12234634e-03 1.42401519e-04]