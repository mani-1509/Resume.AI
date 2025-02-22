function analyze_resume() {
  const fileInput = document.getElementById("resumeFile");
  const jobTitle = document.getElementById("jobTitle").value.trim();
  const company = document.getElementById("company").value.trim();
  const loader = document.getElementById("loader");
  const output = document.getElementById("output");

  if (!fileInput.files.length) {
    alert("Please upload a resume PDF file.");
    return;
  }

  if (!jobTitle || !company) {
    alert("Please enter both the job title and company.");
    return;
  }

  const formData = new FormData();
  formData.append("resume", fileInput.files[0]);
  formData.append("jobTitle", jobTitle);
  formData.append("company", company);

  loader.style.display = "block";
  output.innerHTML = "";

  fetch("/analyze_resume", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      loader.style.display = "none";

      if (data.error) {
        output.innerHTML = `<p style='color:red;'>Error: ${data.error}</p>`;
        return;
      }

      const md = window.markdownit();
      output.innerHTML = md.render(data.choices[0].message.content);

      // Add a "Next" button
      const nextButton = document.createElement("button");
      nextButton.textContent = "Next";
      nextButton.className = "btn btn-primary";
      nextButton.style.marginTop = "20px";
      nextButton.onclick = () => {
        // Send analysis data to the server and redirect to chatbot
        fetch("/store_analysis", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        })
          .then(() => {
            window.location.href = "/chatbot";
          })
          .catch((error) => {
            console.error("Error storing analysis data:", error);
          });
      };
      output.appendChild(nextButton);
    })
    .catch((error) => {
      loader.style.display = "none";
      output.innerHTML = `<p style='color:red;'>An error occurred: ${error.message}</p>`;
    });
}

// GSAP Animations
gsap.from(".hero-text", {
  duration: 1,
  y: 100,
  opacity: 0,
  ease: "power4.out",
});

gsap.from(".feature-card", {
  duration: 0.8,
  y: 50,
  opacity: 0,
  stagger: 0.2,
  ease: "power3.out",
  delay: 0.5,
});
