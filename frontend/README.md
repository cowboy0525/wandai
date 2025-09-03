# 🎨 **Wand AI Frontend - Professional React Application**

## 🚀 **Overview**

The Wand AI Frontend is a **senior-level React application** built with modern best practices, featuring:

- **TypeScript** for type safety and better developer experience
- **Tailwind CSS** for utility-first styling with dark mode support
- **Professional architecture** with proper separation of concerns
- **Error boundaries** and comprehensive error handling
- **Custom hooks** for API operations and state management
- **Theme system** with light/dark mode support
- **Responsive design** for all device sizes
- **Accessibility features** following WCAG guidelines

## 🏗️ **Architecture**

### **Project Structure**
```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (LoadingSpinner, etc.)
│   └── ...             # Feature-specific components
├── contexts/           # React contexts (Theme, etc.)
├── hooks/              # Custom React hooks
├── services/           # API services and utilities
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── App.tsx            # Main application component
```

### **Key Features**
- **Error Boundary**: Catches and handles React errors gracefully
- **Theme Context**: Manages light/dark mode with system preference detection
- **API Service Layer**: Professional HTTP client with interceptors and error handling
- **Custom Hooks**: Reusable logic for API calls, state management, and more
- **Loading States**: Comprehensive loading and error state management
- **Responsive Design**: Mobile-first approach with Tailwind CSS

## 🛠️ **Setup & Installation**

### **Prerequisites**
- **Node.js** 16.0.0 or higher
- **npm** 8.0.0 or higher
- **Backend server** running on `http://localhost:8000`

### **Installation Steps**

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

4. **Open browser** at `http://localhost:3000`

### **Available Scripts**

```bash
# Development
npm start              # Start development server
npm run lint           # Run ESLint
npm run lint:fix       # Fix ESLint errors
npm run format         # Format code with Prettier
npm run type-check     # Run TypeScript type checking

# Production
npm run build          # Build for production
npm run test           # Run tests
```

## 🎨 **UI Components**

### **Base Components**
- **LoadingSpinner**: Multiple sizes and variants
- **Skeleton**: Loading placeholders
- **ProgressBar**: Animated progress indicators
- **LoadingStates**: Comprehensive loading state management

### **Theme System**
- **ThemeProvider**: Context for theme management
- **ThemeToggle**: Button to switch between themes
- **ThemeSelector**: Dropdown for theme selection
- **System preference detection** for automatic theme switching

### **Error Handling**
- **ErrorBoundary**: Catches React errors and displays user-friendly messages
- **Error recovery options** (retry, reload, go home)
- **Error logging** for debugging
- **Copy error details** for support

## 🔌 **API Integration**

### **Service Layer**
```typescript
import { apiService } from './services/api';

// GET request
const data = await apiService.get('/api/v1/endpoint');

// POST request
const result = await apiService.post('/api/v1/endpoint', payload);

// File upload with progress
const uploadResult = await apiService.upload('/api/v1/upload', file, (progress) => {
  console.log(`Upload progress: ${progress}%`);
});
```

### **Custom Hooks**
```typescript
import { useGet, usePost, useUpload } from './hooks/useAPI';

// GET hook with automatic loading states
const { data, loading, error, refetch } = useGet('/api/v1/endpoint');

// POST hook with success/error callbacks
const { execute, loading, error } = usePost('/api/v1/endpoint', {
  onSuccess: (data) => console.log('Success:', data),
  onError: (error) => console.error('Error:', error)
});
```

## 🌙 **Dark Mode Support**

### **Features**
- **Automatic detection** of system preference
- **Manual toggle** between light/dark modes
- **Persistent storage** in localStorage
- **Smooth transitions** between themes
- **CSS variables** for consistent theming

### **Usage**
```typescript
import { useTheme, ThemeToggle } from './contexts/ThemeContext';

function MyComponent() {
  const { theme, isDark, toggleTheme } = useTheme();
  
  return (
    <div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
      <ThemeToggle />
      <p>Current theme: {theme}</p>
    </div>
  );
}
```

## 📱 **Responsive Design**

### **Breakpoints**
- **Mobile**: `< 640px`
- **Tablet**: `640px - 1024px`
- **Desktop**: `> 1024px`

### **Mobile-First Approach**
- All components are designed mobile-first
- Progressive enhancement for larger screens
- Touch-friendly interactions
- Optimized for mobile performance

## ♿ **Accessibility**

### **Features**
- **ARIA labels** and roles
- **Keyboard navigation** support
- **Screen reader** compatibility
- **Focus management** and indicators
- **Color contrast** compliance
- **Semantic HTML** structure

### **WCAG Compliance**
- **Level AA** compliance target
- **Keyboard-only** navigation support
- **Screen reader** optimization
- **High contrast** mode support

## 🧪 **Testing**

### **Testing Strategy**
- **Unit tests** for utility functions
- **Component tests** for UI components
- **Integration tests** for API interactions
- **E2E tests** for critical user flows

### **Running Tests**
```bash
npm test              # Run all tests
npm test -- --watch  # Run tests in watch mode
npm test -- --coverage  # Run tests with coverage
```

## 🚀 **Performance Optimization**

### **Techniques**
- **Code splitting** with React.lazy()
- **Memoization** with React.memo() and useMemo()
- **Debouncing** for search inputs
- **Throttling** for scroll events
- **Lazy loading** for images and components
- **Bundle optimization** with tree shaking

### **Monitoring**
- **Performance metrics** tracking
- **Bundle size** analysis
- **Lighthouse** scores
- **Core Web Vitals** monitoring

## 🔧 **Development Tools**

### **Code Quality**
- **ESLint** for code linting
- **Prettier** for code formatting
- **TypeScript** for type checking
- **Husky** for pre-commit hooks

### **Debugging**
- **React DevTools** integration
- **Error boundary** with detailed error info
- **Console logging** in development
- **Performance profiling** tools

## 📦 **Dependencies**

### **Core Dependencies**
- **React 18** with concurrent features
- **TypeScript 4.9** for type safety
- **Tailwind CSS 3.3** for styling
- **Axios** for HTTP requests

### **UI Libraries**
- **Framer Motion** for animations
- **Lucide React** for icons
- **React Hot Toast** for notifications
- **Recharts** for data visualization

### **Development Dependencies**
- **ESLint** for code quality
- **Prettier** for formatting
- **TypeScript ESLint** for TS-specific rules

## 🌟 **Best Practices**

### **Code Organization**
- **Feature-based** folder structure
- **Consistent naming** conventions
- **Proper separation** of concerns
- **Reusable components** and hooks

### **Performance**
- **Lazy loading** for routes and components
- **Memoization** for expensive calculations
- **Debouncing** for user inputs
- **Optimized re-renders**

### **Security**
- **Input validation** and sanitization
- **XSS prevention** measures
- **CSRF protection** for API calls
- **Secure storage** practices

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Backend Connection Failed**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify proxy configuration in package.json
"proxy": "http://localhost:8000"
```

#### **TypeScript Errors**
```bash
# Run type checking
npm run type-check

# Fix type issues
npm run lint:fix
```

#### **Build Failures**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for dependency conflicts
npm ls
```

### **Performance Issues**
- Check bundle size with `npm run build`
- Analyze with React DevTools Profiler
- Monitor Core Web Vitals
- Optimize images and assets

## 📚 **Additional Resources**

### **Documentation**
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Vite Documentation](https://vitejs.dev/)

### **Learning Resources**
- [React Patterns](https://reactpatterns.com/)
- [TypeScript Best Practices](https://github.com/typescript-eslint/typescript-eslint)
- [Tailwind CSS Components](https://tailwindui.com/)

---

## 🎯 **Next Steps**

1. **Start the backend server** (see main project README)
2. **Install frontend dependencies**: `npm install`
3. **Start development server**: `npm start`
4. **Open browser** at `http://localhost:3000`
5. **Test all features** and report any issues

---

*This frontend is built with enterprise-grade standards and follows industry best practices for React applications.*
