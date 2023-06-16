import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
sys.path.append("..\src")
from summary_functions import  *
from data_extract import *
import streamlit.components.v1 as components

def get_summary(topic):
    
    wikipedia_link = google_search_link(topic)
    if wikipedia_link == "NONE":
        st.write("No Input Given")
        return None
        
    else:
        st.write(f"For following link {wikipedia_link}")
        text = get_wikipedia_text(wikipedia_link)
        summary = summarize_text(text)
        st.table(summary)
        return summary
       
st.title('Generate a TimeLine!')
st.divider()
st.subheader('Enter the topic name')

topic = st.text_input(label = "Enter Topic", max_chars = 20,help = "Enter a topic for which you need to generate a timeline.")
enter_button = st.button("Generate Timeline!")

if enter_button:
    st.write(topic)
    summary = get_summary(topic)
    if summary is not None:
        st.download_button(
            label="Download timeline data as CSV",
            data=summary.to_csv().encode('utf-8'),
            file_name=f'summary_{topic}.csv',
            mime='text/csv',
        )
    components.html('''<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* {
  box-sizing: border-box;
}

body {
  background-color: #f5f6f8;
  font-family: Helvetica, sans-serif;
}

.div1 {
        padding-top : 20px;
        padding-bottom: 20px;
    }

/* The actual timeline (the vertical ruler) */
.timeline {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
}

/* The actual timeline (the vertical ruler) */
.timeline::after {
  content: '';
  position: absolute;
  width: 6px;
  background-color: rgb(103, 100, 100);
  top: 0;
  bottom: 0;
  left: 50%;
  margin-left: -3px;
}

/* Container around content */
.container {
  padding: 10px 40px;
  position: relative;
  background-color: inherit;
  width: 50%;
  /*border: 4px solid #0d0d0d;*/
}

/* The circles on the timeline */
.container::after {
  content: '';
  position: absolute;
  width: 25px;
  height: 25px;
  right: -17px;
  background-color: white;
  border: 4px solid #FF9F55;
  top: 15px;
  border-radius: 50%;
  z-index: 1;
}

/* Place the container to the left */
.left {
  left: 0;
}

/* Place the container to the right */
.right {
  left: 50%;
}

/* Add arrows to the left container (pointing right) */
.left::before {
  content: " ";
  height: 0;
  position: absolute;
  top: 22px;
  width: 0;
  z-index: 1;
  right: 30px;
  border: medium solid rgb(17, 17, 17);
  border-width: 10px 0 10px 10px;
  border-color: transparent transparent transparent rgb(29, 29, 29);
}

/* Add arrows to the right container (pointing left) */
.right::before {
  content: " ";
  height: 0;
  position: absolute;
  top: 22px;
  width: 0;
  z-index: 1;
  left: 30px;
  border: medium solid rgb(31, 30, 30);
  border-width: 10px 10px 10px 0;
  border-color: transparent rgb(19, 19, 19) transparent transparent;
}

/* Fix the circle for containers on the right side */
.right::after {
  left: -16px;
}

/* The actual content */
.content {
  padding: 20px 30px;
  background-color: white;
  position: relative;
  border-radius: 6px;
  border: 2px solid #0d0d0d;
}

/* Media queries - Responsive timeline on screens less than 600px wide */
@media screen and (max-width: 600px) {
  /* Place the timelime to the left */
  .timeline::after {
  left: 31px;
  }
  
  /* Full-width containers */
  .container {
  width: 100%;
  padding-left: 70px;
  padding-right: 25px;
  }
  
  /* Make sure that all arrows are pointing leftwards */
  .container::before {
  left: 60px;
  border: medium solid white;
  border-width: 10px 10px 10px 0;
  border-color: transparent white transparent transparent;
  }

  /* Make sure all circles are at the same spot */
  .left::after, .right::after {
  left: 15px;
  }
  
  /* Make all right containers behave like the left ones */
  .right {
  left: 0%;
  }
}
</style>
<script>
    function displaySearchResult() {
        // Get the input value from the search bar
        var searchTerm = document.getElementById('searchBar').value;
        
        // Update the content on the web page
        var searchResult = document.getElementById('searchResult');
        searchResult.innerHTML = 'You searched for: ' + searchTerm;
    }
</script>
</head>
<body>

    <div class="div1" id="searchContainer">
        <input type="text" id="searchInput" placeholder="Enter search term">
        <button id="searchButton">Search</button>
    </div>

    <div class="div1" id="download">
        <button id="downloadBtn">Download Timeline</button>
    </div>



    <div class="timeline" id="timeline-container"></div>

    <script>
        document.addEventListener("DOMContentLoaded", () => {
            // Fetch events from a file (events.json)
            fetch('events.json')
                .then(response => response.json())
                .then(events => {
                    // Create timeline items dynamically
                    const timelineContainer = document.getElementById('timeline-container');
                    var cnt = 0;

                    events.forEach(event => {

                        if (cnt%2 == 0)
                        {
                            const timelineItem = document.createElement('div');
                            timelineItem.className = 'container left';

                            const content_text = document.createElement('div');
                            content_text.className = 'content';

                            const date = document.createElement('h2');
                            date.textContent = event.date;
                            const summary = document.createElement('p');
                            summary.textContent = event.event;

                            content_text.appendChild(date);
                            content_text.appendChild(summary);

                            timelineItem.appendChild(content_text);

                            timelineContainer.appendChild(timelineItem);
                        }
                        else
                        {
                            const timelineItem = document.createElement('div');
                            timelineItem.className = 'container right';

                            const content_text = document.createElement('div');
                            content_text.className = 'content';

                            const date = document.createElement('h2');
                            date.textContent = event.date;
                            const summary = document.createElement('p');
                            summary.textContent = event.event;

                            content_text.appendChild(date);
                            content_text.appendChild(summary);

                            timelineItem.appendChild(content_text);

                            timelineContainer.appendChild(timelineItem);
                        }
                        cnt += 1
                    });
                });
        });
    </script>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.0/html2canvas.min.js"></script>
    <script>
    // JavaScript
    document.getElementById('downloadBtn').addEventListener('click', function() {
        html2canvas(document.getElementById('timeline-container')).then(function(canvas) {
        // Convert canvas to image URL
        var imageURL = canvas.toDataURL('image/png');
        
        // Create download link
        var downloadLink = document.createElement('a');
        downloadLink.href = imageURL;
        downloadLink.download = 'timeline.png';
        downloadLink.click();
        });
    });

    document.getElementById('searchButton').addEventListener('click', function() {
    var searchTerm = document.getElementById('searchInput').value;
    });
    </script>
<!-- Code injected by live-server -->
<script>
	// <![CDATA[  <-- For SVG support
	if ('WebSocket' in window) {
		(function () {
			function refreshCSS() {
				var sheets = [].slice.call(document.getElementsByTagName("link"));
				var head = document.getElementsByTagName("head")[0];
				for (var i = 0; i < sheets.length; ++i) {
					var elem = sheets[i];
					var parent = elem.parentElement || head;
					parent.removeChild(elem);
					var rel = elem.rel;
					if (elem.href && typeof rel != "string" || rel.length == 0 || rel.toLowerCase() == "stylesheet") {
						var url = elem.href.replace(/(&|\?)_cacheOverride=\d+/, '');
						elem.href = url + (url.indexOf('?') >= 0 ? '&' : '?') + '_cacheOverride=' + (new Date().valueOf());
					}
					parent.appendChild(elem);
				}
			}
			var protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
			var address = protocol + window.location.host + window.location.pathname + '/ws';
			var socket = new WebSocket(address);
			socket.onmessage = function (msg) {
				if (msg.data == 'reload') window.location.reload();
				else if (msg.data == 'refreshcss') refreshCSS();
			};
			if (sessionStorage && !sessionStorage.getItem('IsThisFirstTime_Log_From_LiveServer')) {
				console.log('Live reload enabled.');
				sessionStorage.setItem('IsThisFirstTime_Log_From_LiveServer', true);
			}
		})();
	}
	else {
		console.error('Upgrade your browser. This Browser is NOT supported WebSocket for Live-Reloading.');
	}
	// ]]>
</script>
</body>
</html>
    ''',height = 1000,scrolling = True)

        
 
    
    