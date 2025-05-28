// Example call in script.js
fetch("https://ai-creators-studio-viral.onrender.com/generate", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ prompt: userInput })
})
.then(response => response.json())
.then(data => {
  console.log("Response from backend:", data);
  // Handle video or result
})
.catch(error => console.error("Error:", error));
