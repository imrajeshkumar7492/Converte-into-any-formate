// Error handling utilities
export class ConversionError extends Error {
  constructor(message, code, details = {}) {
    super(message);
    this.name = 'ConversionError';
    this.code = code;
    this.details = details;
  }
}

export class ValidationError extends Error {
  constructor(message, field = null) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}

export class NetworkError extends Error {
  constructor(message, status = null) {
    super(message);
    this.name = 'NetworkError';
    this.status = status;
  }
}

// Error codes
export const ERROR_CODES = {
  // File validation errors
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  UNSUPPORTED_FORMAT: 'UNSUPPORTED_FORMAT',
  INVALID_FILE: 'INVALID_FILE',
  EMPTY_FILE: 'EMPTY_FILE',
  
  // Conversion errors
  CONVERSION_FAILED: 'CONVERSION_FAILED',
  UNSUPPORTED_CONVERSION: 'UNSUPPORTED_CONVERSION',
  QUALITY_TOO_LOW: 'QUALITY_TOO_LOW',
  DIMENSIONS_TOO_LARGE: 'DIMENSIONS_TOO_LARGE',
  
  // Network errors
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  SERVER_ERROR: 'SERVER_ERROR',
  
  // System errors
  STORAGE_FULL: 'STORAGE_FULL',
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
};

// Error messages
export const ERROR_MESSAGES = {
  [ERROR_CODES.FILE_TOO_LARGE]: 'File is too large. Maximum size is 1GB.',
  [ERROR_CODES.UNSUPPORTED_FORMAT]: 'This file format is not supported.',
  [ERROR_CODES.INVALID_FILE]: 'The file appears to be corrupted or invalid.',
  [ERROR_CODES.EMPTY_FILE]: 'The file is empty.',
  [ERROR_CODES.CONVERSION_FAILED]: 'Conversion failed. Please try again.',
  [ERROR_CODES.UNSUPPORTED_CONVERSION]: 'This conversion is not supported.',
  [ERROR_CODES.QUALITY_TOO_LOW]: 'Quality setting is too low for this format.',
  [ERROR_CODES.DIMENSIONS_TOO_LARGE]: 'Image dimensions are too large.',
  [ERROR_CODES.NETWORK_ERROR]: 'Network error. Please check your connection.',
  [ERROR_CODES.TIMEOUT]: 'Request timed out. Please try again.',
  [ERROR_CODES.SERVER_ERROR]: 'Server error. Please try again later.',
  [ERROR_CODES.STORAGE_FULL]: 'Storage is full. Please try again later.',
  [ERROR_CODES.PERMISSION_DENIED]: 'Permission denied.',
  [ERROR_CODES.UNKNOWN_ERROR]: 'An unknown error occurred.'
};

// Error handler class
export class ErrorHandler {
  static handle(error, context = {}) {
    console.error('ErrorHandler caught:', error, context);
    
    // Determine error type and create appropriate error object
    if (error instanceof ConversionError) {
      return this.handleConversionError(error, context);
    } else if (error instanceof ValidationError) {
      return this.handleValidationError(error, context);
    } else if (error instanceof NetworkError) {
      return this.handleNetworkError(error, context);
    } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return this.handleNetworkError(new NetworkError('Network request failed'), context);
    } else {
      return this.handleUnknownError(error, context);
    }
  }

  static handleConversionError(error, context) {
    return {
      type: 'conversion',
      code: error.code,
      message: ERROR_MESSAGES[error.code] || error.message,
      details: error.details,
      context,
      userMessage: this.getUserFriendlyMessage(error.code, context)
    };
  }

  static handleValidationError(error, context) {
    return {
      type: 'validation',
      code: 'VALIDATION_ERROR',
      message: error.message,
      field: error.field,
      context,
      userMessage: error.message
    };
  }

  static handleNetworkError(error, context) {
    return {
      type: 'network',
      code: error.status ? 'NETWORK_ERROR' : 'TIMEOUT',
      message: error.message,
      status: error.status,
      context,
      userMessage: this.getUserFriendlyMessage('NETWORK_ERROR', context)
    };
  }

  static handleUnknownError(error, context) {
    return {
      type: 'unknown',
      code: 'UNKNOWN_ERROR',
      message: error.message || 'An unexpected error occurred',
      context,
      userMessage: 'Something went wrong. Please try again.'
    };
  }

  static getUserFriendlyMessage(code, context) {
    const baseMessage = ERROR_MESSAGES[code] || 'An error occurred';
    
    // Add context-specific information
    if (context.fileName) {
      return `${baseMessage} (File: ${context.fileName})`;
    }
    
    return baseMessage;
  }

  static validateFile(file) {
    const errors = [];
    
    // Check file size (1GB limit)
    if (file.size > 1024 * 1024 * 1024) {
      errors.push(new ValidationError(
        ERROR_MESSAGES[ERROR_CODES.FILE_TOO_LARGE],
        'size'
      ));
    }
    
    // Check if file is empty
    if (file.size === 0) {
      errors.push(new ValidationError(
        ERROR_MESSAGES[ERROR_CODES.EMPTY_FILE],
        'size'
      ));
    }
    
    // Check file type
    const supportedTypes = [
      'image/', 'video/', 'audio/', 'application/pdf',
      'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/', 'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    const isSupported = supportedTypes.some(type => file.type.startsWith(type));
    if (!isSupported && file.name) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      const supportedExtensions = [
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg', 'ico',
        'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'ogv', 'm4v',
        'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma', 'aiff', 'au',
        'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'epub', 'mobi',
        'xls', 'xlsx', 'csv', 'ods', 'ppt', 'pptx', 'odp',
        'zip', 'rar', '7z', 'tar', 'gz', 'bz2'
      ];
      
      if (!supportedExtensions.includes(extension)) {
        errors.push(new ValidationError(
          ERROR_MESSAGES[ERROR_CODES.UNSUPPORTED_FORMAT],
          'type'
        ));
      }
    }
    
    return errors;
  }
}

// Utility function to show error toast
export const showErrorToast = (error, toast) => {
  const errorInfo = ErrorHandler.handle(error);
  
  toast({
    title: "Error",
    description: errorInfo.userMessage,
    variant: "destructive",
    duration: 5000
  });
  
  return errorInfo;
};

// Utility function to show success toast
export const showSuccessToast = (message, toast) => {
  toast({
    title: "Success",
    description: message,
    duration: 3000
  });
};