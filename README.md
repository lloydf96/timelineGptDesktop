# Project Name

[![License](https://img.shields.io/badge/License-GPL-blue.svg)](LICENSE)

## About
Welcome to the Timeline Generator app powered by ChatGPT!
This app is designed to help anyone curious about a subject to create informative timelines quickly and effortlessly. Using the advanced capabilities of ChatGPT, this app can generate timelines based on URLs, specific topics, or your own input text.

### How it Works
The Timeline Generator app leverages the power of ChatGPT to extract key events from the text and arranges them in chronological order to create a coherent timeline.

### Key Features
##### URL-based Timeline: 
Enter the URL of an article or web page, and the app automatically generates a timeline based on the content found in the provided link.

##### Topic-based Timeline: 
Simply input a specific topic, and the app will generate a timeline centered around the topic you specify from Wikipedia.

##### Text-based Timeline: 
If you have your own text describing events or details, you can input it directly, and the app will create a timeline based on your content.

The generated timeline is presented in a clear and accessible format. You can easily view, edit, and download it as a .csv file. The interactive table allows you to modify, add, delete, and rearrange events according to your preference. Once edited, clicking the "Update Timeline" button will instantly reflect your changes in the Timeline Plot.

Additionally, the app provides options to customize the appearance of the timeline. You can change colors and fonts for different elements, making it visually appealing and suitable for your needs. Moreover, you have the option to download the timeline as a .png file for easy sharing or inclusion in your reports or articles.

Note that we have restricted the total number of words to a maximum of 4000. A layer of content moderation was added before passing the text to the API, to make sure that the input text follows the OpenAI content moderation guidelines

##### This repository was curated to make it easy to run the app on local desktop. Follow the following steps to run the streamlit app straight from a local environment using conda or generate a docker image.

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

3. Run the following to generate conda environment
 ```
conda timelinegpt create -f environment.yaml
```
4. Activate the environment
```
conda activate timelinegpt
``` 
5. In the command prompt, navigate to the folder where app.py is located and then run the following to generate the streamlit app.
```
streamlit run app.py
```


Alternatively you may generate a docker image by starting the docker daemon and then running the dockerfile as follows:
```
docker build -t dockerfile .
```


## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Contact

- [Lloyd Fernandes](https://github.com/lloydf96)
- [Praveen Kumar Murugaiah](https://github.com/praveen-kumar-data-science)
- [Raunak Sengupta]

Feel free to reach out if you have any questions, feedback, or suggestions!
