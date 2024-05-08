async function getJSONData(url) {
  const response = await fetch(url);
  // Check for successful response
  if (!response.ok) {
    throw new Error(`Error fetching data: ${response.status}`);
  }
  const jsonData = await response.json();
  return jsonData;
}

const url = "https://api.thingspeak.com/channels/2127654/feeds.json?results=1";

let jsonData; // Declare the variable outside the function

getJSONData(url)
  .then(data => {
    jsonData = data;
    console.log("Fetched JSON data (inside .then):", data);

    // Now you can access jsonData outside the .then block
    console.log("Channel Name:", jsonData["channel"]["name"]);
  })
  .catch(error => {
    console.error("Error:", error);
  });

  console.log(jsonData);


<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Prompt Generator</title>
</head>
<body>
  <h1>AI Generated Prompt</h1>
  <p id="prompt-display"></p>
  <script src="script.js"></script>
</body>
</html>
