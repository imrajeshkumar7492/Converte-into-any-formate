import React, { useState } from 'react';
import { Settings, X, Save, RotateCcw } from 'lucide-react';
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

const AdvancedSettings = ({ isOpen, onClose, settings, onSettingsChange }) => {
  const [localSettings, setLocalSettings] = useState(settings);

  const handleSave = () => {
    onSettingsChange(localSettings);
    onClose();
  };

  const handleReset = () => {
    setLocalSettings({
      imageQuality: 95,
      maxWidth: null,
      maxHeight: null,
      compressionLevel: 'high',
      preserveMetadata: true,
      batchProcessing: true,
      autoDownload: false,
      outputFormat: 'original'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-xl">
              <Settings className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Advanced Settings</h2>
              <p className="text-gray-600">Customize your conversion preferences</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-2"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Settings Content */}
        <div className="p-6 space-y-8">
          {/* Image Quality */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Image Quality</h3>
              <p className="text-sm text-gray-600">Adjust the quality of converted images (1-100)</p>
            </div>
            <div className="space-y-3">
              <Slider
                value={[localSettings.imageQuality]}
                onValueChange={(value) => setLocalSettings({...localSettings, imageQuality: value[0]})}
                max={100}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-sm text-gray-500">
                <span>Low (1)</span>
                <span className="font-medium text-blue-600">{localSettings.imageQuality}%</span>
                <span>High (100)</span>
              </div>
            </div>
          </div>

          {/* Image Dimensions */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Image Dimensions</h3>
              <p className="text-sm text-gray-600">Set maximum width and height for converted images</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Max Width (px)</label>
                <input
                  type="number"
                  value={localSettings.maxWidth || ''}
                  onChange={(e) => setLocalSettings({...localSettings, maxWidth: e.target.value ? parseInt(e.target.value) : null})}
                  placeholder="No limit"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Max Height (px)</label>
                <input
                  type="number"
                  value={localSettings.maxHeight || ''}
                  onChange={(e) => setLocalSettings({...localSettings, maxHeight: e.target.value ? parseInt(e.target.value) : null})}
                  placeholder="No limit"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Compression Level */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Compression Level</h3>
              <p className="text-sm text-gray-600">Choose the compression level for output files</p>
            </div>
            <Select
              value={localSettings.compressionLevel}
              onValueChange={(value) => setLocalSettings({...localSettings, compressionLevel: value})}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low (Larger files, better quality)</SelectItem>
                <SelectItem value="medium">Medium (Balanced)</SelectItem>
                <SelectItem value="high">High (Smaller files, good quality)</SelectItem>
                <SelectItem value="maximum">Maximum (Smallest files)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Processing Options */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Processing Options</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Preserve Metadata</h4>
                  <p className="text-sm text-gray-600">Keep EXIF data, creation dates, and other metadata</p>
                </div>
                <Switch
                  checked={localSettings.preserveMetadata}
                  onCheckedChange={(checked) => setLocalSettings({...localSettings, preserveMetadata: checked})}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Batch Processing</h4>
                  <p className="text-sm text-gray-600">Process multiple files simultaneously</p>
                </div>
                <Switch
                  checked={localSettings.batchProcessing}
                  onCheckedChange={(checked) => setLocalSettings({...localSettings, batchProcessing: checked})}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Auto Download</h4>
                  <p className="text-sm text-gray-600">Automatically download files after conversion</p>
                </div>
                <Switch
                  checked={localSettings.autoDownload}
                  onCheckedChange={(checked) => setLocalSettings({...localSettings, autoDownload: checked})}
                />
              </div>
            </div>
          </div>

          {/* Output Format */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Default Output Format</h3>
              <p className="text-sm text-gray-600">Choose the default format for conversions</p>
            </div>
            <Select
              value={localSettings.outputFormat}
              onValueChange={(value) => setLocalSettings({...localSettings, outputFormat: value})}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="original">Keep original format</SelectItem>
                <SelectItem value="pdf">PDF (for documents)</SelectItem>
                <SelectItem value="png">PNG (for images)</SelectItem>
                <SelectItem value="mp4">MP4 (for videos)</SelectItem>
                <SelectItem value="mp3">MP3 (for audio)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50 rounded-b-3xl">
          <Button
            variant="outline"
            onClick={handleReset}
            className="text-gray-600 border-gray-300 hover:bg-gray-50"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset to Defaults
          </Button>
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={onClose}
              className="text-gray-600 border-gray-300 hover:bg-gray-50"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Settings
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedSettings;