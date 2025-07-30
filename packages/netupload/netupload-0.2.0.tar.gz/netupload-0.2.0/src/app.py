import os
import argparse
import logging
from flask import Flask, request, render_template_string, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

template_string = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <style>
      body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 10px 10px 50px 10px;
        background-color: #f5f5f5;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        overflow: hidden;
      }
      .container {
        background-color: white;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        width: 100%;
        max-width: 600px;
        max-height: 90vh;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
      }
      h2 {
        text-align: center;
        color: #333;
        margin-bottom: 20px;
        font-size: 2.2em;
        font-weight: 300;
      }
      .upload-area {
        border: 2px dashed #ddd;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 15px;
      }
      .upload-area.dragover {
        border-color: #4caf50;
        background-color: #f0f8f0;
      }
      .upload-area:hover {
        border-color: #4caf50;
        background-color: #f9f9f9;
      }
      .file-input {
        display: none;
      }
      .upload-text {
        color: #666;
        font-size: 1.1em;
        margin-bottom: 10px;
      }
      .file-info {
        color: #888;
        font-size: 0.9em;
      }
      .selected-files {
        margin-top: 15px;
        display: none;
        flex-shrink: 1;
        overflow-y: auto;
        max-height: 300px;
      }
      .file-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px;
        border: 1px solid #eee;
        border-radius: 8px;
        margin-bottom: 8px;
        background-color: #fafafa;
      }
      .file-details {
        flex: 1;
      }
      .file-name {
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
      }
      .file-size {
        color: #666;
        font-size: 0.9em;
      }
      .file-status {
        margin-left: 15px;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
      }
      .status-pending {
        background-color: #e3f2fd;
        color: #1976d2;
      }
      .status-uploading {
        background-color: #fff3e0;
        color: #f57c00;
      }
      .status-success {
        background-color: #e8f5e8;
        color: #2e7d32;
      }
      .status-error {
        background-color: #ffebee;
        color: #c62828;
      }
      .progress-container {
        width: 100%;
        margin-top: 10px;
      }
      .progress-bar {
        width: 100%;
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
      }
      .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4caf50, #45a049);
        border-radius: 4px;
        transition: width 0.3s ease;
        width: 0%;
      }
      .progress-text {
        display: flex;
        justify-content: space-between;
        margin-top: 5px;
        font-size: 0.8em;
        color: #666;
      }
      .upload-controls {
        display: flex;
        gap: 10px;
        margin-top: 15px;
      }
      .btn {
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1em;
        font-weight: 500;
        transition: all 0.3s ease;
        flex: 1;
      }
      .btn-primary {
        background-color: #4caf50;
        color: white;
      }
      .btn-primary:hover:not(:disabled) {
        background-color: #45a049;
        transform: translateY(-2px);
      }
      .btn-secondary {
        background-color: #f44336;
        color: white;
      }
      .btn-secondary:hover:not(:disabled) {
        background-color: #da190b;
        transform: translateY(-2px);
      }
      .btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
      }
      .overall-progress {
        margin-top: 15px;
        display: none;
      }
      .overall-progress h3 {
        margin-bottom: 10px;
        color: #333;
      }
      .error-message {
        color: #f44336;
        background-color: #ffebee;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
        display: none;
      }
      .success-message {
        color: #2e7d32;
        background-color: #e8f5e8;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
        display: none;
      }
      .remove-file {
        background: none;
        border: none;
        color: #f44336;
        cursor: pointer;
        font-size: 1.2em;
        margin-left: 10px;
      }
      .remove-file:hover {
        color: #da190b;
      }
      .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 10px 20px;
        text-align: center;
        font-size: 0.85em;
        color: #666;
        background-color: #f5f5f5;
        border-top: 1px solid #eee;
      }
      .footer a {
        color: #666;
        text-decoration: none;
      }
      .footer a:hover {
        color: #333;
        text-decoration: underline;
      }
    </style>
    <title>netupload</title>
  </head>
  <body>
    <div class="container">
      <h2>netupload</h2>
      
      <div class="upload-area" id="uploadArea">
        <div class="upload-text">
          <strong>Click to select files</strong> or drag and drop here
        </div>
        <div class="file-info">
          Supports multiple files • No size limit
        </div>
        <input type="file" id="fileInput" class="file-input" multiple />
      </div>

      <div class="selected-files" id="selectedFiles"></div>

      <div class="upload-controls">
        <button class="btn btn-primary" id="uploadBtn" disabled>Upload Files</button>
        <button class="btn btn-secondary" id="cancelBtn" disabled>Cancel Upload</button>
      </div>

      <div class="overall-progress" id="overallProgress">
        <h3>Upload Progress</h3>
        <div class="progress-container">
          <div class="progress-bar">
            <div class="progress-fill" id="overallProgressFill"></div>
          </div>
          <div class="progress-text">
            <span id="overallProgressText">0%</span>
            <span id="overallProgressFiles">0 / 0 files</span>
          </div>
        </div>
      </div>

      <div class="error-message" id="errorMessage"></div>
      <div class="success-message" id="successMessage"></div>
    </div>
    
    <div class="footer">
      <div>
        <a href="https://github.com/zpg6/netupload" target="_blank">GitHub</a>
        <span> • </span>
        <a href="https://pypi.org/project/netupload/" target="_blank">PyPI</a>
      </div>
    </div>

    <script>
      class UploadManager {
        constructor() {
          this.selectedFiles = [];
          this.fileStates = {}; // Track individual file states: pending, uploading, success, error
          this.activeUploads = [];
          this.uploadArea = document.getElementById('uploadArea');
          this.fileInput = document.getElementById('fileInput');
          this.selectedFilesDiv = document.getElementById('selectedFiles');
          this.uploadBtn = document.getElementById('uploadBtn');
          this.cancelBtn = document.getElementById('cancelBtn');
          this.overallProgress = document.getElementById('overallProgress');
          this.overallProgressFill = document.getElementById('overallProgressFill');
          this.overallProgressText = document.getElementById('overallProgressText');
          this.overallProgressFiles = document.getElementById('overallProgressFiles');
          this.errorMessage = document.getElementById('errorMessage');
          this.successMessage = document.getElementById('successMessage');
          
          this.initEventListeners();
        }

        initEventListeners() {
          this.uploadArea.addEventListener('click', () => this.fileInput.click());
          this.fileInput.addEventListener('change', (e) => this.handleFileSelection(e.target.files));
          this.uploadBtn.addEventListener('click', () => this.startUpload());
          this.cancelBtn.addEventListener('click', () => this.cancelUpload());
          
          // Drag and drop
          this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
          });
          this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
          });
          this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFileSelection(e.dataTransfer.files);
          });
        }

        handleFileSelection(files) {
          this.hideMessages();
          const newFiles = Array.from(files);
          
          // Add new files and set their initial state to pending
          newFiles.forEach(file => {
            const fileId = this.generateFileId(file);
            if (!this.fileStates[fileId]) {
              this.selectedFiles.push(file);
              this.fileStates[fileId] = 'pending';
            }
          });
          
          this.renderSelectedFiles();
          this.updateUploadButton();
        }

        generateFileId(file) {
          // Generate a unique ID based on file name, size, and last modified date
          return `${file.name}-${file.size}-${file.lastModified}`;
        }

        removeFile(index) {
          const file = this.selectedFiles[index];
          const fileId = this.generateFileId(file);
          
          this.selectedFiles.splice(index, 1);
          delete this.fileStates[fileId];
          
          this.renderSelectedFiles();
          this.updateUploadButton();
        }

        renderSelectedFiles() {
          if (this.selectedFiles.length === 0) {
            this.selectedFilesDiv.style.display = 'none';
            return;
          }

          this.selectedFilesDiv.style.display = 'block';
          this.selectedFilesDiv.innerHTML = this.selectedFiles.map((file, index) => {
            const fileId = this.generateFileId(file);
            const state = this.fileStates[fileId] || 'pending';
            const showProgress = state === 'uploading';
            const canRemove = state === 'pending' || state === 'error';
            
            return `
              <div class="file-item" id="file-${index}">
                <div class="file-details">
                  <div class="file-name">${file.name}</div>
                  <div class="file-size">${this.formatFileSize(file.size)}</div>
                  <div class="progress-container" style="display: ${showProgress ? 'block' : 'none'};">
                    <div class="progress-bar">
                      <div class="progress-fill" id="progress-${index}"></div>
                    </div>
                    <div class="progress-text">
                      <span id="progress-text-${index}">0%</span>
                      <span id="progress-speed-${index}"></span>
                    </div>
                  </div>
                </div>
                <div class="file-status status-${state}" id="status-${index}">${this.getStatusText(state)}</div>
                ${canRemove ? `<button class="remove-file" onclick="uploadManager.removeFile(${index})" id="remove-${index}">×</button>` : ''}
              </div>
            `;
          }).join('');
        }

        getStatusText(state) {
          switch(state) {
            case 'pending': return 'Pending';
            case 'uploading': return 'Uploading';
            case 'success': return 'Uploaded';
            case 'error': return 'Error';
            default: return 'Unknown';
          }
        }

        formatFileSize(bytes) {
          const sizes = ['B', 'KB', 'MB', 'GB'];
          if (bytes === 0) return '0 B';
          const i = Math.floor(Math.log(bytes) / Math.log(1024));
          return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
        }

        updateUploadButton() {
          const pendingFiles = this.selectedFiles.filter((file, index) => {
            const fileId = this.generateFileId(file);
            return this.fileStates[fileId] === 'pending';
          });
          
          this.uploadBtn.disabled = pendingFiles.length === 0;
          
          if (pendingFiles.length === 0) {
            this.uploadBtn.textContent = 'Upload Files';
          } else {
            this.uploadBtn.textContent = `Upload ${pendingFiles.length} File${pendingFiles.length > 1 ? 's' : ''}`;
          }
        }

        showError(message) {
          this.errorMessage.textContent = message;
          this.errorMessage.style.display = 'block';
          this.successMessage.style.display = 'none';
        }

        showSuccess(message) {
          this.successMessage.textContent = message;
          this.successMessage.style.display = 'block';
          this.errorMessage.style.display = 'none';
        }

        hideMessages() {
          this.errorMessage.style.display = 'none';
          this.successMessage.style.display = 'none';
        }

        async startUpload() {
          const pendingFiles = this.selectedFiles.filter((file, index) => {
            const fileId = this.generateFileId(file);
            return this.fileStates[fileId] === 'pending';
          });
          
          if (pendingFiles.length === 0) return;

          this.hideMessages();
          this.uploadBtn.disabled = true;
          this.cancelBtn.disabled = false;
          this.overallProgress.style.display = 'block';
          
          let completedFiles = 0;
          const totalFiles = pendingFiles.length;
          
          // Update overall progress
          this.overallProgressFiles.textContent = `${completedFiles} / ${totalFiles} files`;
          
          try {
            // Upload only pending files sequentially to avoid overwhelming the server
            for (let i = 0; i < pendingFiles.length; i++) {
              const file = pendingFiles[i];
              const fileIndex = this.selectedFiles.indexOf(file);
              await this.uploadFile(file, fileIndex);
              completedFiles++;
              
              const overallPercent = Math.round((completedFiles / totalFiles) * 100);
              this.overallProgressFill.style.width = `${overallPercent}%`;
              this.overallProgressText.textContent = `${overallPercent}%`;
              this.overallProgressFiles.textContent = `${completedFiles} / ${totalFiles} files`;
            }
            
            this.showSuccess(`Successfully uploaded ${totalFiles} file(s)!`);
          } catch (error) {
            this.showError(`Upload failed: ${error.message}`);
          } finally {
            this.updateUploadButton();
            this.cancelBtn.disabled = true;
          }
        }

        uploadFile(file, index) {
          return new Promise((resolve, reject) => {
            const fileId = this.generateFileId(file);
            
            // Skip if already uploaded
            if (this.fileStates[fileId] === 'success') {
              resolve();
              return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            const xhr = new XMLHttpRequest();
            this.activeUploads.push(xhr);
            
            // Update file status
            this.fileStates[fileId] = 'uploading';
            const statusEl = document.getElementById(`status-${index}`);
            const progressContainer = document.querySelector(`#file-${index} .progress-container`);
            const progressFill = document.getElementById(`progress-${index}`);
            const progressText = document.getElementById(`progress-text-${index}`);
            const progressSpeed = document.getElementById(`progress-speed-${index}`);
            const removeBtn = document.getElementById(`remove-${index}`);
            
            if (statusEl) {
              statusEl.textContent = 'Uploading';
              statusEl.className = 'file-status status-uploading';
            }
            if (progressContainer) progressContainer.style.display = 'block';
            if (removeBtn) removeBtn.style.display = 'none';
            
            let startTime = Date.now();
            let startLoaded = 0;
            
            xhr.upload.addEventListener('progress', (e) => {
              if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressFill.style.width = `${percent}%`;
                progressText.textContent = `${percent}%`;
                
                // Calculate upload speed
                const currentTime = Date.now();
                const timeElapsed = (currentTime - startTime) / 1000;
                const bytesLoaded = e.loaded - startLoaded;
                const speed = bytesLoaded / timeElapsed;
                
                if (timeElapsed > 1) {
                  progressSpeed.textContent = `${this.formatFileSize(speed)}/s`;
                  startTime = currentTime;
                  startLoaded = e.loaded;
                }
              }
            });
            
            xhr.onload = () => {
              if (xhr.status === 200) {
                try {
                  const response = JSON.parse(xhr.responseText);
                  this.fileStates[fileId] = 'success';
                  if (statusEl) {
                    statusEl.textContent = 'Uploaded';
                    statusEl.className = 'file-status status-success';
                  }
                  if (progressFill) progressFill.style.width = '100%';
                  if (progressText) progressText.textContent = '100%';
                  if (progressSpeed) progressSpeed.textContent = 'Complete';
                  this.renderSelectedFiles(); // Re-render to hide remove button
                  resolve(response);
                } catch (e) {
                  this.fileStates[fileId] = 'success';
                  if (statusEl) {
                    statusEl.textContent = 'Uploaded';
                    statusEl.className = 'file-status status-success';
                  }
                  if (progressFill) progressFill.style.width = '100%';
                  if (progressText) progressText.textContent = '100%';
                  if (progressSpeed) progressSpeed.textContent = 'Complete';
                  this.renderSelectedFiles(); // Re-render to hide remove button
                  resolve();
                }
              } else {
                try {
                  const response = JSON.parse(xhr.responseText);
                  this.fileStates[fileId] = 'error';
                  if (statusEl) {
                    statusEl.textContent = 'Error';
                    statusEl.className = 'file-status status-error';
                  }
                  if (progressSpeed) progressSpeed.textContent = 'Failed';
                  this.renderSelectedFiles(); // Re-render to show remove button
                  reject(new Error(response.error || `Server error: ${xhr.status}`));
                } catch (e) {
                  this.fileStates[fileId] = 'error';
                  if (statusEl) {
                    statusEl.textContent = 'Error';
                    statusEl.className = 'file-status status-error';
                  }
                  if (progressSpeed) progressSpeed.textContent = 'Failed';
                  this.renderSelectedFiles(); // Re-render to show remove button
                  reject(new Error(`Server error: ${xhr.status}`));
                }
              }
            };
            
            xhr.onerror = () => {
              this.fileStates[fileId] = 'error';
              if (statusEl) {
                statusEl.textContent = 'Error';
                statusEl.className = 'file-status status-error';
              }
              if (progressSpeed) progressSpeed.textContent = 'Failed';
              this.renderSelectedFiles(); // Re-render to show remove button
              reject(new Error('Network error'));
            };
            
            xhr.onabort = () => {
              this.fileStates[fileId] = 'error';
              if (statusEl) {
                statusEl.textContent = 'Cancelled';
                statusEl.className = 'file-status status-error';
              }
              if (progressSpeed) progressSpeed.textContent = 'Cancelled';
              this.renderSelectedFiles(); // Re-render to show remove button
              reject(new Error('Upload cancelled'));
            };
            
            xhr.open('POST', '/');
            xhr.send(formData);
          });
        }

        cancelUpload() {
          this.activeUploads.forEach(xhr => xhr.abort());
          this.activeUploads = [];
          this.updateUploadButton();
          this.cancelBtn.disabled = true;
          this.showError('Upload cancelled by user');
        }
      }

      // Initialize the upload manager when the page loads
      const uploadManager = new UploadManager();
    </script>
  </body>
</html>
"""


def save_files(files, save_directory):
    """Save uploaded files to the specified directory with enhanced error handling."""
    
    # Create the save directory if it does not exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    saved_files = []
    
    # Save each file to the specified directory
    for file in files:
        if file.filename == '':
            continue
            
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        if not filename:
            continue
            
        # Handle filename conflicts by adding a counter
        original_filename = filename
        counter = 1
        while os.path.exists(os.path.join(save_directory, filename)):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            counter += 1
        
        file_path = os.path.join(save_directory, filename)
        
        try:
            file.save(file_path)
            saved_files.append({
                'original_name': file.filename,
                'saved_name': filename,
                'size': os.path.getsize(file_path)
            })
            logging.info(f"Successfully saved file: {filename}")
        except Exception as e:
            logging.error(f"Error saving file {filename}: {str(e)}")
            raise
    
    return saved_files


@app.route("/", methods=["GET", "POST"])
def upload_files():
    if request.method == "POST":
        try:
            files = request.files.getlist("file")
            
            if not files or all(file.filename == '' for file in files):
                return jsonify({"error": "No files provided"}), 400
            
            saved_files = save_files(files, app.config["SAVE_DIRECTORY"])
            
            return jsonify({
                "message": "Files uploaded successfully!",
                "files": saved_files,
                "count": len(saved_files)
            }), 200
            
        except Exception as e:
            logging.error(f"Upload error: {str(e)}")
            return jsonify({"error": "Upload failed. Please try again."}), 500

    return render_template_string(template_string)


def run_server():
    parser = argparse.ArgumentParser(description="File Upload Server")
    parser.add_argument(
        "--save-dir",
        type=str,
        default="./uploads",
        help="Directory to save uploaded files",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to run the Flask server. `0.0.0.0` is recommended to make the server accessible from all network interfaces.",
    )
    parser.add_argument(
        "--port", type=int, default=4000, help="Port to run the Flask server. Any available port can be used."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('netupload.log'),
            logging.StreamHandler()
        ]
    )

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)

    app.config["SAVE_DIRECTORY"] = args.save_dir

    logging.info(f"Starting netupload server on {args.host}:{args.port}")
    logging.info(f"Files will be saved to: {os.path.abspath(args.save_dir)}")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    run_server()
