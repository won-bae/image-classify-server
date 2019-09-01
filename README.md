# TNC Image Classification Server
Image classification with Web API and UI.<br>
It's is written in Django and React along with Tensorflow. Image classification model is based on MegaDetector v3 model from [https://github.com/microsoft/CameraTraps].

## Setup
There are three different setups needed to be done for Django, React and model parts, respectively.

### Model setup
Install python packages and download megadetector_v3.pb
```
$ cd /path/to/this/repo
$ bash setup.sh
```

### Django setup
```
$ cd /path/to/this/repo
$ cd tf_inception
```
In settings.py, add ALLOWED_HOSTS and CORS_ORIGIN_WHITELIST. For CORS_ORIGIN_WHITELIST, add the host name with port number. For example, 'http://website.com:7018'

### React setup
```
$ cd /path/to/this/repo
$ cd react/webpack
```
In webpack.config.dev.js, add port number and host in devServer. For example, port: 7018, host: 'website.com'. Notice that the port number used in this setup should be different from the one used in Django.


## Usage

To run the server on localhost,

```
$ cd /path/to/this/repo
$ python manage.py collectstatic
$ python manage.py runserver
```

In the different terminal window,
```
$ npm run start
```


#### Input
Parameter | Type                           | Description
--------- | ------------------------------ | -----------------------------------------------------------------------------------
image     | file                           | Image file that you want to classify.
image64   | text                           | Image in base64 form that you want to classify. Currently supports JPEG images only
k         | text<br>(optional, default=10) | Return top-k categories of the results. Must me string in integer format.

Note: you need to send either 'image' or 'image64'

#### Result
Parameter    | Type                | Description
------------ | ------------------- | --------------------------------------------
success      | bool                | Whether classification was sucessfuly or not
confidence   | category, float     | pair of category and it's confidence

Note: *category* is not paramater name but string of the category.<br>
Example:  {"success": true, "confidence": {  "mongoose": 0.87896, "hare": 0.00123 }}
