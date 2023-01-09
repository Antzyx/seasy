# Assignment - Seasy
### TL;DR

As evidenced by the length of the following README, I tend to be somewhat thorough. As an apology, I present to you this
summary.

The problem formulation is heavily under-constrained, and a single test sample is given. Therefore, the assignment is 
either trivial (if no generalisation is required) or impossible to achieve without a very flexible method (if 
generalisation is expected but no further data nor instruction is available). Traditional methods are not very flexible and 
depend on sensitive hyper-parameters. As a consequence, since instance segmentation is well-studied, we choose to go for
a fine-tuning of a state-of-the-art deep model.

The model is trained on rendered synthetic data, generated based on assumptions made on the problem. It is tested on the
hand-labeled provided sample. We choose Mask-RCNN [1] as a well-studied model available with robust implementations for 
fine-tuning and inference.

After 1 epochs on 5394 synthetic images, all candies are detected and are attributed masks with the following IoUs 
(overall 0.96) :
- M&Ms : 0.97
- M&Ms with nuts : 0.96
- Skittles : 0.95
- Jelly beans : 0.95

Finally, classification shows the following confusion matrix :

|   | M | N | S  | B |
|---|---|---|----|---|
| M | 1 | 0 | 6  | 1 |
| N | 0 | 8 | 0  | 0 |
| S | 1 | 0 | 14 | 0 |
| S | 0 | 0 | 1  | 8 |
This shows a general accuracy of 77.5%. Generally speaking, M&Ms with nuts and beans are expectedly very well classified. 
Also expectedly, skittles are very hard to distinguish from M&Ms because of their close resemblance, and the lack of
trademarks in the generated textures.

The algorithm can easily be improved. Simply improving the rendering script with trademarks should greatly affect the
model in its capacity to tell skittles from M&Ms. Longer training might also improve some of the last
mis-classified candies. Some of them, however, might remain challenging, as even myself as the annotator remained unsure
of their class.

### Problem formulation

#### The problem
An image is provided, showing candies of 4 types on a table. The picture is taken from above, and specularities indicate
ambient lighting from a strong spot and possibly windows.

Additional data is given pertaining to the 4 types of candy, supposed to help in classifying them. It is asked to 
perform instance segmentation on the candies and to classify them between "mms", "mms_nut", "skittle" and "bean".

#### Assumptions
- Given that the problem is obviously a toy task, it is assumed that there is no broader context pertaining to the task.
  The following reasoning would rarely hold in any real-world context, where inquiring about the scope and context of 
  the project would provide the necessary constraints
- Given that it would be trivial with most method to segment and classify a unique image, it is assumed that the method 
  should generalise to an undefined distribution of similar images
- we assume that the method should generalise on pictures of those 4 types on candies placed on a surface. Since no 
  rule was provided for generalisation, we choose to let the kind of surface, number of candies and overall lighting 
  conditions variables of the problem
  
#### Issues
Since only a single image is provided, and generalisability is still most likely expected, most traditional or simple
methods might not work. Indeed, those methods often have numerous very important hyper-parameters which cannot be found
reliably from a single sample. What's more, the problem is extremely under-constrained, and no real-world context exists
to clarify it. Therefore, the method to solve this problem should be flexible and powerful, because simple methods tend
to struggle with problems presenting many factors of variation.

Of course, this leads to a second issue : although complex methods are permissive and more robust to common noise and 
variations, they do also require a larger amount of data for training purposes.

### Exploratory process

#### Verifying that traditional methods are unsuited for the problem
We start by trying out several methods and assessing their sensitivity to their hyper-parameters. This sensitivity is
crucial : it would denote a brittleness to unexpected variations. Therefore, methods with sensitive hyper-parameters are
discarded. We test different kinds of processing. Frequency analysis shows no particular angle from which to simplify
the problem. Common edge detection such as Canny proves very parameter-dependent, as well as automatic detection methods
for the numbers of clusters in clustering methods, such as the commonly used elbow method. Pixel-based k-means and 
watershed-based methods similarly yield poor results, even with oracle numbers of clusters. HSV decomposition does not
seem to tremendously ease the task, and traditional shadow-removal methods to leverage hue more accurately are also 
based on some important parameters. Finally, out-of-the-box deep detectors fail as well due to not having adequate 
classes in their training. COCO-trained models, for instance, only detect the orange-ish candies (as oranges).

#### Evaluating suitability of deep methods
Checking out the state of the art for deep methods, most methods there seem to adequately solve problems orders of
magnitude more complicated than segmenting candies on a flat surface. Therefore, it seems that most current 
architectures such as the current SOTA (EVA) or longstanding staples such as YOLO or Mask-RCNN [1] would work if they could
be retrained with relevant data.

Acquiring sufficient data here might not ba as hard as it seems. The main morphological characteristics of the candies 
are known and simple. Large quantities of OBJ files representing random candies of each type should be simple to 
synthesise and sufficiently different from each other to be distinguished by the model.

#### Drawing an experimental plan
There was no hardware constraint for the assignment, but given the time constraints it seems important to limit the size
of the model to be able to iterate slightly. In addition, it is likely that the amount of data that can be rendered in
such a short time would remain around 10^4-5, therefore also justifying the use of a small model. The large models of 
those classes are anyways largely over-parametrised for the simpler problem at hands here. There is also little time for
long experiments, which also speaks for using a well-understood and proved architecture (and hence not the SOTA one).

There are 7 days allocated. 2 days will be used to create the code for data generation. 2 days will be used to prepare
the training and evaluation code while the data is generated. This will leave 3 days to experiment with the model. If
the data generation turns out to be faulty, there will be no time to sample another dataset, but the general approach 
chosen still seems like the best one considering the constraints and assumptions made. Besides, in my personal
experience, dense tasks such as segmentation suffer less from distribution shifts such as those common between 
generated and real data, and fewer samples are required to reach good results. However, training times may be long.
This also means that the results after 7 days are unlikely to be the asymptotical results achievable by the model. The
training time will be used to prepare evaluation and to document the code. If some time is left, effort will be spent in
post-processing.

### Experiments
#### Data generation
The generation code can be found in the data_generation folder. We use a blender script to generate OBJ files for random
candies. Then, we use the blenderproc [3] python library to render scenes and create data in a format similar to the COCO
dataset, which should prove useful to set up the retraining of the models. Experiments to improve the realism are
orchestrated using my own configuration system, YAECS [5]. The surface is simulated by random images taken from the PASS
[6] dataset, which is a dataset of random pictures taken from around the world.
The following elements seem to be mis-represented :
- the ground surface has no roughness, and therefore also no specularity (this should be alleviated by the fact that all 
  variations in images used is vastly superior to a conventional tabletop variation)
- the surface of the candies lack roughness as well, which could have been simulated using normal maps but were not for 
  a lack of time
- the texture of the candies do not feature the trademarks "s" and "m", also due to a lack of time. This might actually
  to be a real issue at test time
- lighting is approximated by two random sources, which is vastly inferior to a real environment

Although quite general, this data generation still makes some assumptions :
- the camera will always be positioned in a roughly similar manner as the one in the provided sample (from above, 
  looking roughly straight down towards the center of the pile of candies, at approximately the same distance)
- the lighting will never be extreme (otherwise the specularity of the involved surfaces would make the task very hard)
- the ground surface is flat
- there may be slight occlusions, but there is only one layer of candies

#### Training
We use the model Mask-RCNN [1], trained using the repo MMDet [2]. Experiments are orchestrated using the provided configuration 
system. The one image provided is hand-annotated to serve as a test, but cannot of course be used as either training or 
validation. For validation, we use the same data as for training. This may seem counter-intuitive, but it makes sense in
this context for the following reasons : 
- since both the validation and training data are generated, we already know that they are sampled from the
same distribution, so monitoring the correctness of this specific assumption need not be done
- Mask-RCNN [1] is a well-studied model, whose generalisation capabilities have been proven many times
- the generalisation capabilities that a validation split would ascertain are only a very small subset of the 
  interesting ones anyways
- the model will be fine-tuned from weights obtained using a very large dataset, COCO, and the fine-tuning will be short
  (just a few epochs), therefore limiting the influence of overfitting
- there will be no time for significant iteration over the model, therefore questioning the relevance of a "validation"
phase in the first place
- and finally, while previous arguments have shown the little use that this validation would have, producing it would 
  still have a cost, which we thus decide we am unwilling to pay considering the expected returns
  
#### Post-processing
Based on prior insight and first validation results, we design the following post-processing scheme ahead of testing.
First, if 2 bounding boxes have an IoU exceeding 0.8, they are considered to be the same object. This is viable because
spreading this amount of candies with such shapes on a tabletop is very unlikely to generate the kind of occlusions that
would lead to a case where two candies have a 0.8 IoU. If those two bounding boxes predicted different classes, priority
is given to M&Ms and Jelly Bean detections rather than using the predicted scores. Indeed, in my experience, such scores
are very hard to correlate and cannot be used lightly. On the contrary, validation classification scores show a 
dominance of M&Ms with nuts and skittles, therefore the model is considered biased in this direction.

In addition to the box disambiguation, we add a simple clustering method to avoid obvious mis-classification. Indeed,
scale might be hard to grasp for the model because it is made variable during data generation (the camera height is
random), therefore we hypothesise that shape and texture are a more determining factor. If we assume that the picture
will always present a mix of the 4 classes, then we can assume that the comparatively larger candies will always be
M&Ms with nuts. Therefore, among the detected segmentation masks, we cluster the areas of the candies using 3-means.
The largest is assumed to represent M&Ms with nuts, and for any segmentation belonging to this cluster we overwrite the
class to be M&Ms with nuts. Then, for any of the other 2 clusters, we reclassify any mask in those clustered such that
any of those masks predicted as M&Ms with nuts by the model is changed to jelly bean instead. This is because jelly 
beans are similar in shape as M&Ms with nuts, so if the model learns some scale invariance this is the most likely
mis-classification it could make.

#### Test and metrics
The most usually reported metric for this task is mAP (mean average precision), however, this is a research metric 
mostly used to have a single value for comparison between different models. In particular, it is designed to account for
segmentations maps being potentially hard to register with one object of interest, or multiple ones being assigned to 
one object. It is also meant to combine proper classification and detection. In this case, we do not need such a generic 
metric. In particular, we know from visual assessment that all bounding box are easily, uniquely assigned to one 
annotation. In addition, after using our post-processing, only one bounding box remain for each annotation. Therefore,
we can simply consider for each annotation the IoU between the ground truth and the detection (if it exists). This is
much simpler to interpret and contains all the required information about detection in our simplified case. In addition,
we can use a confusion matrix to report classification results, and finally report the number of undetected objects. 
Using these three very simple metrics gives us a full view of the detector's ability, while ignoring the unneeded 
complexity of the "traditional" metric.

#### Prior expectations
Before seeing any results, the following assumptions can be made. First, we assume that the segmentation and detection
should end up being very good. This is because in our experience, it is very frequent for dense tasks to adapt very well 
from synthetic data (even little) to real one, therefore we do not expect issues there.

Second, we assume that the classification will present more of a challenge. Indeed, the synthetic data ignores important
visual cues that can be used to differentiate candies, in particular textural details such as trademarks (M&Ms and 
skittles) and dots (jelly beans). Without those cues, differentiating candies becomes reliant on shape and dimensions.
Since camera position is partially randomised, the scale information that can be relied on is mostly relative in nature,
which cannot be leveraged by Mask-RCNN architectures. In addition, M&Ms and skittles have very similar shapes when 
viewed from above (they are mainly distinguishable by their height). We assume that our post-processing scheme should 
solve most issues with jelly beans and M&Ms with nuts, but expect remaining classification errors between M&Ms and 
skittles.

#### Results
We annotate the provided image using Coco Annotator [7], which allows us to compute quantitative metrics to enrich our
visual assessment. After 1 epochs on 5394 synthetic images, all candies are detected and are attributed masks with the
following IoUs (overall 0.96) :
- M&Ms : 0.97
- M&Ms with nuts : 0.96
- Skittles : 0.95
- Jelly beans : 0.95

Finally, we construct the following confusion matrix by hand :

|   | M | N | S  | B |
|---|---|---|----|---|
| M | 1 | 0 | 6  | 1 |
| N | 0 | 8 | 0  | 0 |
| S | 1 | 0 | 14 | 0 |
| S | 0 | 0 | 1  | 8 |
This shows a general accuracy of 77.5%. Generally speaking, M&Ms with nuts and beans are expectedly very well classified. 
Also expectedly, skittles are very hard to distinguish from M&Ms because of their close resemblance, and the lack of
trademarks in the generated textures.

### Further work
Several improvements can be made to the current pipeline to make it more precise and more robust. Here, we present a few
ideas that can improve the detector and classifier.
1) additional test data can bring to light more subtle differences between the synthetic and real distributions which
can help fix the current model
2) adding black as a potential colour for candies is expected to help detection slightly
3) complexifying the texturisation scheme for the synthetic candies (mainly adding dots/trademarks) is expected to
   significantly boost classification
4) post-processing might benefit from more complex heuristics, including maybe some depth estimation to take candy 
   height into account
   
### Conclusion
The chosen approach seems conclusive. After just a few days, the detection results are almost on human-level. The 
classification results remain sub-par for some classes, but simple steps can be taken to most likely gain further
improvements. Importantly, those results were obtained without any prior data besides domain knowledge and theoretical
reflexion, leaving the provided image to be used exclusively for testing. The fact that the learnt algorithm still
performed well implies that the proposed method is likely to generalize well within the stated assumptions.

### Reproducing the results
#### STEP 1 : generate obj files for the candies
Download blender [4], open it then go to Edit > Preferences > Add-ons. Look for the Add-on "Add mesh: Extra Objects" and
activate it. Then, go to the python distribution of your blender installation and install the YAECS [5] package there.

Go to `configs/config.yaml` and change the `data_folder` path to a path of your choice. This path will be used to 
generate your assets and data.

Finally, go to `scripts/generate_objs.bat` and change the paths such that they correspond to your installation. The 
first path is the path to the blender executable on your computer. The second path is the absolute path to the file 
`data_generation/candy_generator_script.py`. You might want to run the command directly if you are on linux, rather than
changing the batch script to a shell script.

#### STEP 2 : generate renderings
Install blenderproc [3] and YAECS [5] in your python environment, then go to blenderproc's blender installation (might
be different from your computer's blender installation) and install YAECS [5] there too.

Download the first tar file of the PASS [6] dataset and untar it to a file of your choice, then put the absolute path to
that file in the `image_rendering.pass_path` parameter of the config `configs/config.yaml`.

Finally, go to `scripts/generate_renders.bat` and change the paths such that they correspond to your installation. The 
first path is the path to the repo for the project. The second and third paths are the absolute paths to the conda
executable file (if your python environment is not created with conda, make sure the code uses the proper environment).
The fourth path is the absolute path to `data_generation/render.py`. You might want to run the command directly if you
are on linux, rather than changing the batch script to a shell script.

This script will generate 10 000 samples. You may stop it at any time and start it again to resume. You may launch it
several times in a row to generate more than 10 000 samples. It is ill-advised to start it several times in parallel. We 
let it run until we have 5394 images.

#### STEP 3 : correct the annotations
From the project repo's root, run the script `scripts/adapt_annotations.py` with your python environment.

#### STEP 4 : fine-tune and use the model
From the project repo's root, clone the MMDet repository [2] and follow its instructions for installation. Create a new
folder in `mmdetection/configs` named `candies`, and place the two following config files in this folder:
- the training config (`configs/mask_rcnn_r50_caffe_fpn_mstrain-poly_1x_candies.py`)
- the inference config (`configs/mask_rcnn_r50_caffe_fpn_mstrain-poly_1x_candies_infer.py`)

Then, for fine-tuning, first replace `mmdetection/mmdet/datasets/pipelines/transforms.py` with our own version 
(`src/transforms.py`) then go to the mmdetection folder and run the following script for however many epochs you wish : 
`python tools\train.py configs\candies\mask_rcnn_r50_caffe_fpn_mstrain-poly_1x_candies.py`. You might have to change
folder separators on Linux. The results we present are obtained after 1 epoch of training. The logs and weights are 
stored under `work_dirs/mask_rcnn_r50_caffe_fpn_mstrain-poly_1x_candies`.

To perform inference on the provided image, first replace `mmdetection/mmdet/core/visualization/image.py` with our own
version (`src/image.py`) to integrate our specific post-processing. Then, use the following command :

`python demo/image_demo.py <PATH TO IMAGE> configs/candies/mask_rcnn_r50_caffe_fpn_mstrain-poly_1x_candies_infer.py
work_dirs/mask_rcnn_r50_caffe_fpn_mstrain-poly_1x_candies/latest.pth --device cpu
--out-file work_dirs/mask_rcnn_r50_caffe_fpn_mstrain-poly_1x_candies/result.jpg`

You may use provided weights for this purpose, which constitute our version of the detector (`model.pth`).

### References
[1] Mask R-CNN, He et al., https://arxiv.org/abs/1703.06870

[2] MMDetection, Chen et al., https://arxiv.org/abs/1906.07155, https://github.com/open-mmlab/mmdetection

[3] BlenderProc, Denninger et al., https://arxiv.org/abs/1911.01911, https://github.com/DLR-RM/BlenderProc

[4] blender, https://www.blender.org/

[5] YAECS, https://gitlab.com/reactivereality/public/yaecs

[6] PASS: An ImageNet replacement for self-supervised pretraining without humans, Asano et al.,
https://arxiv.org/abs/2109.13228, https://www.robots.ox.ac.uk/~vgg/data/pass/

[7] COCO Annotator, Justin Brooks, https://github.com/jsbroks/coco-annotator/