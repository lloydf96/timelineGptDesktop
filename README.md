# Project Name

[![License](https://img.shields.io/badge/License-GPL-blue.svg)](LICENSE)

## Description

This repository was curated to make it easy to run the app on local desktop. Follow the following steps to run the streamlit app straight from a local environment using conda or generate a docker image.

## Table of Contents

## Installation
1. Clone the repo
2. Create a ```/.streamlit``` folder and add the following files

   a. ```config.toml``` :

   Copy the following in this file
    ```
      [theme]
      base="light"
      primaryColor="#143aa2"
      secondaryBackgroundColor="#cfe8ff"
      textColor="#0b3081"
      ```
    
    b. ```secrets.toml``` :

   Copy the following in this file
    ```
    chatgpt_api = "your api key"
    ```

4. Run the following to generate conda environment
 ```
conda timelinegpt create -f environment.yaml
```
3. Activate the environment
```
conda activate timelinegpt
``` 
4. In the command prompt, navigate to the folder where app.py is located and then run the following to generate the streamlit app.
```
streamlit run app.py
```

Alternatively you may generate a docker image by starting the docker daemon and then running the dockerfile as follows:
```
docker build -t dockerfile .
```


## Usage

Explain how to use the project or provide examples of its usage. Include code snippets or screenshots if applicable. You can also link to a separate documentation file if available.

## Contributing

Specify how others can contribute to the project. Include guidelines for submitting bug reports, feature requests, or pull requests. If you have a code of conduct, mention it here.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Contact

- [Lloyd Fernandes](https://github.com/lloydf96)
- [Praveen Kumar Murugaiah](https://github.com/praveen-kumar-data-science)
- [Raunak Sengupta]

Feel free to reach out if you have any questions, feedback, or suggestions!
