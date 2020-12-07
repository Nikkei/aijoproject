[Open with Colab](https://colab.research.google.com/github/Nikkei/aijoproject/blob/main/insight-gender/insight_gender_share.ipynb

# Dependency 

This tools depends on the library [InsightFace](https://github.com/deepinsight/insightface)

The code of InsightFace can be used under MIT License, but the trained model in the repository is research purpose only.

___face_model_aijo.py___ is the modified module of face_model.py in InsightFace repository

___mtcnn_detector_aijo.py___ is the modified module of mtcnn_detector.py in InsightFace repository


# Preparation 

## create a CSV file
create a CSV file with these columns

* article_id / unique id for each article
* top_image_url / url for each image or image file name in the image folder

You can add any other columns which you might use later for the analysis

## create folders

create images folder under the folder your notebook is placed.
If you want to use pre-downloaded images, place images in the images folder

create output folder under the folder your notebook is placed.

create another images folder under the output folder you created.

The folder structure would be like this

* insight_gender_share.ipynb
    * images/
    * output/
        * images/

# Setup
recommend python 3.8 environment

```
pip install -r requirements.txt
```

clone insightface repository
``` 
git clone --recursive https://github.com/deepinsight/insightface.git
cp -r insightface/gender-age/* .
```

Start jupyter
```
jupyter notebook
```

Run `insight_gender_share.ipynb` in your jupyter environment

