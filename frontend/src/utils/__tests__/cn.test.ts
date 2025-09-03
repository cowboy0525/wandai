import {
  cn,
  formatBytes,
  formatDate,
  debounce,
  throttle,
  generateId,
  safeJsonParse,
  deepClone,
  deepEqual,
  capitalize,
  toTitleCase,
  truncateText,
  isValidEmail,
  isValidUrl,
  sleep,
  retryWithBackoff,
} from '../cn';

describe('cn (class name utility)', () => {
  it('combines multiple class names', () => {
    const result = cn('class1', 'class2', 'class3');
    expect(result).toBe('class1 class2 class3');
  });

  it('handles conditional classes', () => {
    const isActive = true;
    const isDisabled = false;
    const result = cn(
      'base-class',
      isActive && 'active',
      isDisabled && 'disabled'
    );
    expect(result).toBe('base-class active');
  });

  it('handles arrays of classes', () => {
    const result = cn(['class1', 'class2'], 'class3');
    expect(result).toBe('class1 class2 class3');
  });

  it('handles objects with boolean values', () => {
    const result = cn({
      'base-class': true,
      'active': true,
      'disabled': false,
    });
    expect(result).toBe('base-class active');
  });

  it('handles mixed input types', () => {
    const result = cn(
      'base',
      ['array1', 'array2'],
      { 'obj1': true, 'obj2': false },
      'string',
      null,
      undefined
    );
    expect(result).toBe('base array1 array2 obj1 string');
  });
});

describe('formatBytes', () => {
  it('formats bytes correctly', () => {
    expect(formatBytes(0)).toBe('0 Bytes');
    expect(formatBytes(1024)).toBe('1.0 KB');
    expect(formatBytes(1048576)).toBe('1.0 MB');
    expect(formatBytes(1073741824)).toBe('1.0 GB');
  });

  it('handles custom decimal places', () => {
    expect(formatBytes(1024, 0)).toBe('1 KB');
    expect(formatBytes(1048576, 3)).toBe('1.000 MB');
  });

  it('handles edge cases', () => {
    expect(formatBytes(500)).toBe('500.0 Bytes');
    expect(formatBytes(1536)).toBe('1.5 KB');
  });
});

describe('formatDate', () => {
  it('formats dates with default options', () => {
    const date = new Date('2024-01-15T10:30:00Z');
    const result = formatDate(date);
    expect(result).toMatch(/Jan 15, 2024/);
  });

  it('formats dates with custom options', () => {
    const date = new Date('2024-01-15T10:30:00Z');
    const result = formatDate(date, { 
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    expect(result).toBe('January 15, 2024');
  });

  it('handles string dates', () => {
    const result = formatDate('2024-01-15T10:30:00Z');
    expect(result).toMatch(/Jan 15, 2024/);
  });

  it('handles invalid dates gracefully', () => {
    const result = formatDate('invalid-date');
    expect(result).toMatch(/Invalid Date/);
  });
});

describe('debounce', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('debounces function calls', () => {
    const func = jest.fn();
    const debouncedFunc = debounce(func, 100);

    debouncedFunc();
    debouncedFunc();
    debouncedFunc();

    expect(func).not.toHaveBeenCalled();

    jest.advanceTimersByTime(100);
    expect(func).toHaveBeenCalledTimes(1);
  });

  it('resets timer on subsequent calls', () => {
    const func = jest.fn();
    const debouncedFunc = debounce(func, 100);

    debouncedFunc();
    jest.advanceTimersByTime(50);
    debouncedFunc();
    jest.advanceTimersByTime(50);
    expect(func).not.toHaveBeenCalled();

    jest.advanceTimersByTime(100);
    expect(func).toHaveBeenCalledTimes(1);
  });
});

describe('throttle', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('throttles function calls', () => {
    const func = jest.fn();
    const throttledFunc = throttle(func, 100);

    throttledFunc();
    throttledFunc();
    throttledFunc();

    expect(func).toHaveBeenCalledTimes(1);

    jest.advanceTimersByTime(100);
    throttledFunc();
    expect(func).toHaveBeenCalledTimes(2);
  });
});

describe('generateId', () => {
  it('generates unique IDs', () => {
    const id1 = generateId('test');
    const id2 = generateId('test');
    const id3 = generateId('other');

    expect(id1).not.toBe(id2);
    expect(id1).toMatch(/^test_\d+_[a-z0-9]+$/);
    expect(id3).toMatch(/^other_\d+_[a-z0-9]+$/);
  });

  it('uses default prefix when none provided', () => {
    const id = generateId();
    expect(id).toMatch(/^id_\d+_[a-z0-9]+$/);
  });
});

describe('safeJsonParse', () => {
  it('parses valid JSON', () => {
    const result = safeJsonParse('{"key": "value"}', {});
    expect(result).toEqual({ key: 'value' });
  });

  it('returns fallback for invalid JSON', () => {
    const fallback = { default: true };
    const result = safeJsonParse('invalid json', fallback);
    expect(result).toBe(fallback);
  });

  it('handles malformed JSON', () => {
    const fallback = { default: true };
    const result = safeJsonParse('{"key": "value"', fallback);
    expect(result).toBe(fallback);
  });
});

describe('deepClone', () => {
  it('clones primitive values', () => {
    expect(deepClone(42)).toBe(42);
    expect(deepClone('string')).toBe('string');
    expect(deepClone(true)).toBe(true);
    expect(deepClone(null)).toBe(null);
  });

  it('clones objects deeply', () => {
    const original = {
      a: 1,
      b: { c: 2, d: [3, 4] },
      e: new Date('2024-01-01'),
    };
    const cloned = deepClone(original);

    expect(cloned).toEqual(original);
    expect(cloned).not.toBe(original);
    expect(cloned.b).not.toBe(original.b);
    expect(cloned.b.d).not.toBe(original.b.d);
    expect(cloned.e).not.toBe(original.e);
  });

  it('clones arrays deeply', () => {
    const original = [1, [2, 3], { a: 4 }];
    const cloned = deepClone(original);

    expect(cloned).toEqual(original);
    expect(cloned).not.toBe(original);
    expect(cloned[1]).not.toBe(original[1]);
    expect(cloned[2]).not.toBe(original[2]);
  });

  it('handles circular references gracefully', () => {
    const original: any = { a: 1 };
    original.self = original;

    // Should not throw
    expect(() => deepClone(original)).not.toThrow();
  });
});

describe('deepEqual', () => {
  it('compares primitive values', () => {
    expect(deepEqual(1, 1)).toBe(true);
    expect(deepEqual('string', 'string')).toBe(true);
    expect(deepEqual(true, true)).toBe(true);
    expect(deepEqual(null, null)).toBe(true);
    expect(deepEqual(1, 2)).toBe(false);
    expect(deepEqual('a', 'b')).toBe(false);
  });

  it('compares objects deeply', () => {
    const obj1 = { a: 1, b: { c: 2 } };
    const obj2 = { a: 1, b: { c: 2 } };
    const obj3 = { a: 1, b: { c: 3 } };

    expect(deepEqual(obj1, obj2)).toBe(true);
    expect(deepEqual(obj1, obj3)).toBe(false);
  });

  it('compares arrays deeply', () => {
    const arr1 = [1, [2, 3], { a: 4 }];
    const arr2 = [1, [2, 3], { a: 4 }];
    const arr3 = [1, [2, 3], { a: 5 }];

    expect(deepEqual(arr1, arr2)).toBe(true);
    expect(deepEqual(arr1, arr3)).toBe(false);
  });

  it('compares dates', () => {
    const date1 = new Date('2024-01-01');
    const date2 = new Date('2024-01-01');
    const date3 = new Date('2024-01-02');

    expect(deepEqual(date1, date2)).toBe(true);
    expect(deepEqual(date1, date3)).toBe(false);
  });

  it('handles different types', () => {
    expect(deepEqual({}, [])).toBe(false);
    expect(deepEqual(null, undefined)).toBe(false);
    expect(deepEqual(1, '1')).toBe(false);
  });
});

describe('capitalize', () => {
  it('capitalizes first letter and lowercases rest', () => {
    expect(capitalize('hello')).toBe('Hello');
    expect(capitalize('WORLD')).toBe('World');
    expect(capitalize('tEsT')).toBe('Test');
  });

  it('handles single characters', () => {
    expect(capitalize('a')).toBe('A');
    expect(capitalize('Z')).toBe('Z');
  });

  it('handles empty string', () => {
    expect(capitalize('')).toBe('');
  });
});

describe('toTitleCase', () => {
  it('converts string to title case', () => {
    expect(toTitleCase('hello world')).toBe('Hello World');
    expect(toTitleCase('this is a test')).toBe('This Is A Test');
    expect(toTitleCase('UPPER CASE')).toBe('Upper Case');
  });

  it('handles single word', () => {
    expect(toTitleCase('hello')).toBe('Hello');
  });

  it('handles empty string', () => {
    expect(toTitleCase('')).toBe('');
  });
});

describe('truncateText', () => {
  it('truncates text to specified length', () => {
    expect(truncateText('Hello world', 5)).toBe('He...');
    expect(truncateText('Hello world', 8)).toBe('Hello...');
  });

  it('returns original text if shorter than max length', () => {
    expect(truncateText('Hello', 10)).toBe('Hello');
  });

  it('uses custom suffix', () => {
    expect(truncateText('Hello world', 5, '***')).toBe('He***');
  });

  it('handles empty string', () => {
    expect(truncateText('', 5)).toBe('');
  });
});

describe('isValidEmail', () => {
  it('validates correct email formats', () => {
    expect(isValidEmail('test@example.com')).toBe(true);
    expect(isValidEmail('user.name@domain.co.uk')).toBe(true);
    expect(isValidEmail('test+tag@example.org')).toBe(true);
  });

  it('rejects invalid email formats', () => {
    expect(isValidEmail('invalid-email')).toBe(false);
    expect(isValidEmail('@example.com')).toBe(false);
    expect(isValidEmail('test@')).toBe(false);
    expect(isValidEmail('test@.com')).toBe(false);
    expect(isValidEmail('')).toBe(false);
  });
});

describe('isValidUrl', () => {
  it('validates correct URL formats', () => {
    expect(isValidUrl('https://example.com')).toBe(true);
    expect(isValidUrl('http://localhost:3000')).toBe(true);
    expect(isValidUrl('ftp://files.example.org')).toBe(true);
    expect(isValidUrl('https://example.com/path?param=value')).toBe(true);
  });

  it('rejects invalid URL formats', () => {
    expect(isValidUrl('not-a-url')).toBe(false);
    expect(isValidUrl('http://')).toBe(false);
    expect(isValidUrl('')).toBe(false);
  });
});

describe('sleep', () => {
  it('delays execution for specified time', async () => {
    const start = Date.now();
    await sleep(100);
    const end = Date.now();
    
    expect(end - start).toBeGreaterThanOrEqual(100);
  });
});

describe('retryWithBackoff', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('retries failed operations with exponential backoff', async () => {
    let attempts = 0;
    const failingFunction = jest.fn().mockImplementation(() => {
      attempts++;
      if (attempts < 3) {
        throw new Error('Failed');
      }
      return 'Success';
    });

    const promise = retryWithBackoff(failingFunction, 3, 100);
    
    // Fast-forward through retries
    jest.advanceTimersByTime(100); // First retry
    jest.advanceTimersByTime(200); // Second retry
    
    const result = await promise;
    
    expect(result).toBe('Success');
    expect(failingFunction).toHaveBeenCalledTimes(3);
  });

  it('throws error after max retries', async () => {
    const failingFunction = jest.fn().mockRejectedValue(new Error('Always fails'));

    const promise = retryWithBackoff(failingFunction, 2, 100);
    
    // Fast-forward through retries
    jest.advanceTimersByTime(100); // First retry
    jest.advanceTimersByTime(200); // Second retry
    
    await expect(promise).rejects.toThrow('Always fails');
    expect(failingFunction).toHaveBeenCalledTimes(3);
  });

  it('succeeds on first attempt', async () => {
    const successfulFunction = jest.fn().mockResolvedValue('Success');

    const result = await retryWithBackoff(successfulFunction, 3, 100);
    
    expect(result).toBe('Success');
    expect(successfulFunction).toHaveBeenCalledTimes(1);
  });
});
