# File Converter - Iframe Version

A streamlined file converter designed specifically for iframe embedding. This version contains only the core conversion functionality without headers, footers, or marketing content.

## Features

- **Core File Conversion**: Upload and convert files between 40+ formats
- **Iframe-Friendly**: Compact design optimized for embedding
- **Static Deployment**: Frontend-only solution suitable for GitHub Pages
- **Mock Conversions**: Demonstrates conversion workflow (for demo purposes)
- **Responsive Design**: Works on desktop and mobile devices

## Supported Formats

- **Images**: JPG, PNG, WEBP, BMP, TIFF, GIF, PDF, ICO, SVG
- **Documents**: PDF, DOC, DOCX, TXT, RTF, ODT
- **Videos**: MP4, AVI, MOV, WMV, FLV, MKV, WEBM
- **Audio**: MP3, WAV, FLAC, AAC, OGG, M4A, WMA, AIFF

## Usage

### Iframe Embedding

```html
<iframe 
  src="https://yourusername.github.io/your-repo-name/" 
  width="800" 
  height="600" 
  frameborder="0"
  title="File Converter">
</iframe>
```

### Responsive Iframe

```html
<div style="position: relative; width: 100%; padding-bottom: 75%; height: 0;">
  <iframe 
    src="https://yourusername.github.io/your-repo-name/" 
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
    title="File Converter">
  </iframe>
</div>
```

## Deployment

This project is configured to automatically deploy to GitHub Pages when you push to the main/master branch.

### Setup Instructions

1. **Fork/Clone this repository**
2. **Enable GitHub Pages**:
   - Go to your repository Settings
   - Navigate to "Pages" section
   - Set Source to "GitHub Actions"
3. **Push to main branch** - The GitHub Actions workflow will automatically build and deploy

### Manual Build

If you want to build locally:

```bash
cd frontend
yarn install
yarn build
```

The built files will be in the `frontend/build` directory.

## Customization

### Styling
- Edit `frontend/src/components/IframeHeroSection.jsx` for UI changes
- Modify Tailwind classes for styling adjustments

### Functionality
- Add real backend integration by updating the API calls
- Modify supported formats in the `getSupportedFormats` function
- Add real file conversion by integrating with a backend service

## Notes

- This version uses **mock conversions** for demonstration purposes
- For real file conversion, integrate with a backend service
- The interface is optimized for iframe embedding with minimal overhead
- All styling is self-contained with no external dependencies

## License

MIT License - feel free to use and modify as needed.