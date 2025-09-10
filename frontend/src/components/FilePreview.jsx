import React, { useState, useEffect } from 'react';
import { X, Download, Eye, FileText, Image, Video, Music, Archive } from 'lucide-react';
import { Button } from './ui/button';

const FilePreview = ({ file, isOpen, onClose, onDownload }) => {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [previewType, setPreviewType] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (file && isOpen) {
      generatePreview();
    }
    
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [file, isOpen]);

  const generatePreview = () => {
    setLoading(true);
    
    try {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      
      // Determine preview type
      if (file.type.startsWith('image/')) {
        setPreviewType('image');
      } else if (file.type.startsWith('video/')) {
        setPreviewType('video');
      } else if (file.type.startsWith('audio/')) {
        setPreviewType('audio');
      } else if (file.type.startsWith('text/')) {
        setPreviewType('text');
      } else {
        setPreviewType('file');
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      setPreviewType('file');
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = () => {
    if (file.type.startsWith('image/')) return <Image className="w-8 h-8 text-green-500" />;
    if (file.type.startsWith('video/')) return <Video className="w-8 h-8 text-blue-500" />;
    if (file.type.startsWith('audio/')) return <Music className="w-8 h-8 text-purple-500" />;
    if (file.type.startsWith('text/')) return <FileText className="w-8 h-8 text-orange-500" />;
    return <Archive className="w-8 h-8 text-gray-500" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isOpen || !file) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            {getFileIcon()}
            <div>
              <h2 className="text-xl font-bold text-gray-900 truncate max-w-md">
                {file.name}
              </h2>
              <p className="text-sm text-gray-600">
                {formatFileSize(file.size)} • {file.type || 'Unknown type'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {onDownload && (
              <Button
                onClick={onDownload}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl"
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 p-2"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Preview Content */}
        <div className="p-6 max-h-[calc(90vh-120px)] overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Preview */}
              {previewType === 'image' && previewUrl && (
                <div className="text-center">
                  <img
                    src={previewUrl}
                    alt={file.name}
                    className="max-w-full max-h-96 mx-auto rounded-lg shadow-lg"
                    onError={() => setPreviewType('file')}
                  />
                </div>
              )}

              {previewType === 'video' && previewUrl && (
                <div className="text-center">
                  <video
                    src={previewUrl}
                    controls
                    className="max-w-full max-h-96 mx-auto rounded-lg shadow-lg"
                    onError={() => setPreviewType('file')}
                  >
                    Your browser does not support video preview.
                  </video>
                </div>
              )}

              {previewType === 'audio' && previewUrl && (
                <div className="text-center">
                  <audio
                    src={previewUrl}
                    controls
                    className="w-full max-w-md mx-auto"
                    onError={() => setPreviewType('file')}
                  >
                    Your browser does not support audio preview.
                  </audio>
                </div>
              )}

              {previewType === 'text' && previewUrl && (
                <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {loading ? 'Loading...' : 'Text preview not available'}
                  </pre>
                </div>
              )}

              {previewType === 'file' && (
                <div className="text-center py-12">
                  <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    {getFileIcon()}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Preview not available
                  </h3>
                  <p className="text-gray-600">
                    This file type cannot be previewed in the browser.
                  </p>
                </div>
              )}

              {/* File Information */}
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">File Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Name:</span>
                    <p className="text-gray-600 truncate">{file.name}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Size:</span>
                    <p className="text-gray-600">{formatFileSize(file.size)}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Type:</span>
                    <p className="text-gray-600">{file.type || 'Unknown'}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Last Modified:</span>
                    <p className="text-gray-600">{formatDate(file.lastModified)}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FilePreview;