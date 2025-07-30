# TwelveLabs Python SDK

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-Built%20with%20Fern-brightgreen)](https://buildwithfern.com?utm_source=github&utm_medium=github&utm_campaign=readme&utm_source=https%3A%2F%2Fgithub.com%2Ffern-demo%2Ftwelve-labs-python)
[![PyPI version](https://img.shields.io/pypi/v/twelvelabs.svg)](https://pypi.org/project/twelvelabs/)

This SDK provides a convenient way to interact with the Twelve Labs Video Understanding Platform from an application written in the Python language. The SDK equips you with a set of intuitive classes and methods that streamline the process of interacting with the platform, minimizing the need for boilerplate code.

# Prerequisites

Ensure that the following prerequisites are met before using the SDK:

- [Python](https://www.python.org) 3.7 or newer must be installed on your machine.
- You have an API key. If you don't have an account, please [sign up](https://playground.twelvelabs.io/) for a free account. Then, to retrieve your API key, go to the [API Key](https://playground.twelvelabs.io/dashboard/api-key) page, and select the **Copy** icon to the right of the key to copy it to your clipboard.

# Install the SDK

Install the `twelvelabs` package:

```sh
pip install twelvelabs
```

The current SDK version is compatible with API version 1.3. If you wish to use API version 1.2, please use version 0.3.x or earlier of the SDK. Below are the SDK versions and the corresponding supported API versions.

| SDK Version | Supported API Version |
| ----------- | --------------------- |
| 1.0.x       | 1.3                   |
| 0.4.x       | 1.3                   |
| 0.3.x       | 1.2                   |

How to install the latest 0.3.x version of the SDK:

```sh
pip install twelvelabs<0.4.0
```

How to install the SDK with a specific version:

```sh
pip install twelvelabs==0.3.x # replace 0.3.x with the version you want
```

# Initialize the SDK

1. Import the SDK into your application:

   ```py
   from twelvelabs import TwelveLabs
   ```

2. Instantiate the SDK client with your API key. This example code assumes that your API key is stored in an environment variable named `TWELVELABS_API_KEY`:

   ```py
   client = TwelveLabs(api_key=os.getenv('TWELVELABS_API_KEY'))
   ```

# Use the SDK

To get started with the SDK, follow these basic steps:

1. Create an index.
2. Upload videos.
3. Perform downstream tasks, such as searching or generating text from video.

## Create an index

To create an index, use the example code below, replacing "<YOUR_INDEX_NAME>" with the desired name for your index:

```py
from twelvelabs import TwelveLabs
from twelvelabs.indexes import IndexesCreateRequestModelsItem

try:
    index_obj = client.indexes.create(
        index_name="<YOUR_INDEX_NAME>",
        models=[
            IndexesCreateRequestModelsItem(
                model_name="marengo2.7",
                model_options=["visual", "audio"],
            ),
            IndexesCreateRequestModelsItem(
                model_name="pegasus1.2",
                model_options=["visual", "audio"],
            ),
        ],
    )
    print(index_obj)
except Exception as e:
    print(f"Error: {e}")
```

Note the following about this example:

- The platform provides two distinct model types - embedding and generative, each serving unique purposes in multimodal video understanding.
  - **Embedding models (Marengo)**: These models are proficient at performing tasks such as search and classification, enabling enhanced video understanding.
  - **Generative models (Pegasus)**: These models generate text based on your videos.
    For your index, both Marengo and Pegasus are enabled.
- The `model_options` fields specify the types of information each video understanding model will process.
- The models and the model options specified when you create an index apply to all the videos you upload to that index and cannot be changed. For details, see the [model options](https://docs.twelvelabs.io/v1.3/docs/model-options) page.

The output should look similar to the following:

```
IndexesCreateResponse(id='65b1b926560f741da96836d7')
```

Note that the API returns, among other information, a field named `id`, representing the unique identifier of your new index.

For a description of each field in the request and response, see the [Create an index](https://docs.twelvelabs.io/v1.3/reference/create-index) page.

## Upload videos

Before you upload a video to the platform, ensure that it meets the following requirements:

- **Video resolution**: Must be at least 480x360 or 360x480, and not exceed 4K (3840x2160).
- **Video and audio formats**: The video files you wish to upload must be encoded in the video and audio formats listed on the [FFmpeg Formats Documentation](https://ffmpeg.org/ffmpeg-formats.html) page. For videos in other formats, contact us at [support@twelvelabs.io](mailto:support@twelvelabs.io).
- **Duration**: For Marengo, it must be between 4 seconds and 2 hours (7,200s). For Pegasus, it must be between 4 seconds and 1 hour (3,600s).
- **File size**: Must not exceed 2 GB. If you require different options, send us an email at support@twelvelabs.io.
- **Audio track**: If the `audio` [model option](https://docs.twelvelabs.io/v1.3/docs/model-options) is selected, the video you're uploading must contain an audio track.

To upload videos, use the example code below, replacing the following:

- **`<YOUR_VIDEO_PATH>`**: with a string representing the path to the directory containing the video files you wish to upload.
- **`<YOUR_INDEX_ID>`**: with a string representing the unique identifier of the index to which you want to upload your video.

```py
from glob import glob

video_files = glob("<YOUR_VIDEO_PATH>") # Example: "/videos/*.mp4"
for video_file in video_files:
  print(f"Uploading {video_file}")
  task = client.tasks.create(index_id="<YOUR_INDEX_ID>", video_file=video_file)
  print(f"Task id={task.id}")

  # (Optional) Monitor the video indexing process
  # Utility function to print the status of a video indexing task
  def on_task_update(task):
          print(f"  Status={task.status}")

  # You can implement task monitoring here
  print(f"Uploaded {video_file}. The unique identifer of your video is {task.video_id}.")
```

Note that once a video has been successfully uploaded and indexed, the response will contain a field named `video_id`, representing the unique identifier of your video.

For a description of each field in the request and response, see the [Create a video indexing task](https://docs.twelvelabs.io/reference/create-video-indexing-task) page.

## Perform downstream tasks

The sections below show how you can perform the most common downstream tasks. See [our documentation](https://docs.twelvelabs.io/docs) for a complete list of all the features the Twelve Labs Understanding Platform provides.

### Search

To search for relevant video content, you can use either text or images as queries:

- **Text queries**: Use natural language to find video segments matching specific keywords or phrases.
- **Image queries**: Use images to find video segments that are semantically similar to the provided images.

**Search using text queries**

To perform a search request using text queries, use the example code below, replacing the following:

- **`<YOUR_INDEX_ID>`**: with a string representing the unique identifier of your index.
- **`<YOUR_QUERY>`**: with a string representing your search query. Note that the API supports full natural language-based search. The following examples are valid queries: "birds flying near a castle," "sun shining on water," and "an officer holding a child's hand."
- **`[<YOUR_SEARCH_OPTIONS>]`**: with an array of strings that specifies the sources of information the platform uses when performing a search. For example, to search based on visual and audio cues, use `["visual", "audio"]`. Note that the search options you specify must be a subset of the model options used when you created the index. For more details, see the [Search options](https://docs.twelvelabs.io/docs/search-options) page.

```py
search_results = client.search.create(
  index_id="<YOUR_INDEX_ID>",
  query_text="<YOUR_QUERY>",
  search_options=["<YOUR_SEARCH_OPTIONS>"]
)

# Utility function to print a specific page
def print_page(page):
  for clip in page:
    print(
        f" video_id={clip.video_id} score={clip.score} start={clip.start} end={clip.end} confidence={clip.confidence}"
    )

print_page(search_results.data)

# Get next page using page_token if available
if hasattr(search_results, 'page_info') and search_results.page_info and search_results.page_info.next_page_token:
    next_page = client.search.retrieve(search_results.page_info.next_page_token)
    print_page(next_page.data)
```

The results are returned one page at a time, with a default limit of 10 results on each page. You can retrieve the next page using the `page_token` from the response.

```
 video_id=65ca2bce48db9fa780cb3fa4 score=84.9 start=104.9375 end=111.90625 confidence=high
 video_id=65ca2bce48db9fa780cb3fa4 score=84.82 start=160.46875 end=172.75 confidence=high
 video_id=65ca2bce48db9fa780cb3fa4 score=84.77 start=55.375 end=72.46875 confidence=high
```

Note that the response contains, among other information, the following fields:

- `video_id`: The unique identifier of the video that matched your search terms.
- `score`: A quantitative value determined by the AI model representing the level of confidence that the results match your search terms.
- `start`: The start time of the matching video clip, expressed in seconds.
- `end`: The end time of the matching video clip, expressed in seconds.
- `confidence`: A qualitative indicator based on the value of the score field. This field can take one of the following values:
  - `high`
  - `medium`
  - `low`

For a description of each field in the request and response, see the [Make any-to-video search requests](/reference/any-to-video-search) page.

**Search using image queries**

You can provide images as local files or publicly accessible URLs. Use the `query_media_file` parameter for local image files and the `query_media_url` parameter for publicly accessible URLs.

To perform a search request using image queries, use the example code below, replacing the following:

- **`<YOUR_INDEX_ID>`**: with a string representing the unique identifier of your index.
- **`<YOUR_FILE_PATH>`**: with a string representing the path of the image file you wish to provide.
- **`[<YOUR_SEARCH_OPTIONS>]`**: with an array of strings that specifies the sources of information the platform uses when performing a search. For example, to search based on visual cues, use `["visual"]`. Note that the search options you specify must be a subset of the model options used when you created the index. For more details, see the [Search options](https://docs.twelvelabs.io/docs/search-options) page.

```python
search_results = client.search.create(
    index_id="<YOUR_INDEX_ID>",
    query_media_type="image",
    query_media_file="<YOUR_FILE_PATH>", # Use query_media_url instead to provide a file from a publicly accessible URL.
    search_options=["<YOUR_SEARCH_OPTIONS>"]
)
```

The response is similar to that received when using text queries.

### Generate text from video

The Twelve Labs Video Understanding Platform offers three distinct endpoints tailored to meet various requirements. Each endpoint has been designed with specific levels of flexibility and customization to accommodate different needs.

Note the following about using these endpoints:

- The Pegasus video understanding model must be enabled for the index to which your video has been uploaded.
- Your prompts must be instructive or descriptive, and you can also phrase them as questions.
- The maximum length of a prompt is 1500 characters.

#### Summaries, chapters, and highlights

To generate summaries, chapters, and highlights, use the example code below, replacing the following:

- **`<YOUR_VIDEO_ID>`**: with a string representing the unique identifier of your video.
- **`<TYPE>`**: with a string representing the type of text the platform should generate. This parameter can take one of the following values: "summary", "chapter", or "highlight".
- _(Optional)_ **`<YOUR_PROMPT>`**: with a string that provides context for the summarization task, such as the target audience, style, tone of voice, and purpose. Example: "Generate a summary in no more than 5 bullet points."

```py
res = client.summarize(video_id="<YOUR_VIDEO_ID>", type="<TYPE>", prompt="<YOUR_PROMPT>")
if res.summarize_type == "summary":
    print(f"{res.summary}")
elif res.summarize_type == "chapter":
    print(f"Chapters: {res.chapters}")
elif res.summarize_type == "highlight":
    print(f"Highlights: {res.highlights}")
```

For a description of each field in the request and response, see the [Summaries, chapters, or highlights](https://docs.twelvelabs.io/v1.3/docs/generate-summaries-chapters-highlights) page.

#### Open-ended analysis

To generate open-ended analysis, use the example code below, replacing the following:

- **`<YOUR_VIDEO_ID>`**: with a string representing the unique identifier of your video.
- **`<YOUR_PROMPT>`**: with a string that guides the model on the desired format or content. The maximum length of the prompt is 1500 characters. Example: "I want to generate a description for my video with the following format: Title of the video, followed by a summary in 2-3 sentences, highlighting the main topic, key events, and concluding remarks."

```py
res = client.analyze(video_id="<YOUR_VIDEO_ID>", prompt="<YOUR_PROMPT>")
print(f"{res.data}")
```

## Error Handling

The SDK includes a set of exceptions that are mapped to specific HTTP status codes, as shown in the table below:

| Exception                | HTTP Status Code |
| ------------------------ | ---------------- |
| BadRequestError          | 400              |
| AuthenticationError      | 401              |
| PermissionDeniedError    | 403              |
| NotFoundError            | 404              |
| ConflictError            | 409              |
| UnprocessableEntityError | 422              |
| RateLimitError           | 429              |
| InternalServerError      | 5xx              |

The following example shows how you can handle specific HTTP errors in your application:

```python
import os
from twelvelabs import TwelveLabs
from twelvelabs.errors import BadRequestError, NotFoundError

client = TwelveLabs(api_key=os.getenv("TWELVELABS_API_KEY"))
try:
    indexes = client.indexes.list()
    print(indexes)
except BadRequestError as e:
    print("Bad request.")
except NotFoundError as e:
    print("Not found.")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
