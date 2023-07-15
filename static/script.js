document.getElementById("fileInput").addEventListener("change", async function () {
  const fileInput = document.getElementById("fileInput");
  const previewImg = document.getElementById("previewImg");
  const predictionText = document.getElementById("prediction");

  if (fileInput.files && fileInput.files[0]) {
    const reader = new FileReader();

    reader.onload = async function (e) {
      previewImg.setAttribute("src", e.target.result);
      previewImg.style.display = "block";
      document.getElementById("result").style.display = "block";

      const formData = new FormData();
      formData.append("file", fileInput.files[0]);

      try {
        const response = await fetch("/predict/", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        predictionText.innerText = `${data.label}`;
      } catch (error) {
        console.error("Error while processing the request:", error);
        predictionText.innerText = "Error occurred. Please try again.";
      }
    };

    reader.readAsDataURL(fileInput.files[0]);
  } else {
    previewImg.style.display = "none";
    document.getElementById("result").style.display = "none";
  }
});
