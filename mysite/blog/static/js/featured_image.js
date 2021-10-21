function getImages(content) {
  const regex = new RegExp(`<img.*?src="(.*?)"`, 'g')
  let match = regex.exec(content);
  let images = []
  while (match !== null) {
    images.push(match[1]);
    match = regex.exec(content);
  }
  return images;
}

function featured_image_handler(event) {
  const allImagesElement = document.getElementById("images")
  allImagesElement.textContent = '';

  const content = document.getElementById("id_content").value;
  if (content) {
    const selector = document.getElementById("featured_image_selector")
    selector.className = 'active'
    let images = getImages(content);
    if (!images) {
      const span = document.createElement('span')
      span.innerText = "No images found in the post. Please add an image first."
      allImagesElement.appendChild(span)
      return;
    }

    for (const i of images){
      const div = document.createElement('div')
      const img = document.createElement('img')
      img.src = i
      div.appendChild(img)
      div.addEventListener("click", function () {
        const selected = document.getElementById('id_featured_image')
        if (selected)
          selected.value = img.src
          selector.style.display = 'none'
          allImagesElement.textContent = '';
      })
      allImagesElement.appendChild(div)
    }
  } else {
    const span = document.createElement('span')
    span.innerText = "No images found in the post. Please add an image first."
    allImagesElement.appendChild(span)
  }
}

document.getElementById("post_form").addEventListener("submit", ()=>{
  const selectedImage = document.getElementById("id_featured_image")
  if (!selectedImage.value) {
    const content = document.getElementById("id_content").value;
    if (!content) return true;
    const images = getImages()
    if (images.length) selectedImage.value = images[0];
    return true;
  }
})