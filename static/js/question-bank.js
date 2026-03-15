function openViewer(element) {
    const fileUrl = element.getAttribute("data-file");
    const frame = document.getElementById("pdfFrame");
    const viewer = document.getElementById("pdf-viewer-section");

    frame.src = fileUrl;
    viewer.style.display = "block";

    window.scrollTo({
        top: viewer.offsetTop,
        behavior: "smooth"
    });
}

function closeViewer() {
    const frame = document.getElementById("pdfFrame");
    const viewer = document.getElementById("pdf-viewer-section");

    frame.src = "";
    viewer.style.display = "none";
}