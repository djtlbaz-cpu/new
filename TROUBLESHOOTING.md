# Beat Addicts DAW - Troubleshooting & Debug Guide

## Common Issues and Solutions

### 1. White Screen / Blank Page

**Symptoms:**
- App loads but shows only a white page
- No content visible

**Causes & Solutions:**

#### A. Component Import Errors
\`\`\`bash
# Check browser console (F12) for errors like:
# "Failed to resolve module specifier"
# "Cannot find module"
\`\`\`

**Solution:**
1. Ensure all UI components exist in `src/components/ui/`
2. Check import paths in `App.jsx`
3. Verify component exports match imports

#### B. Missing Dependencies
\`\`\`bash
# Check for missing node_modules
npm install
\`\`\`

#### C. Build Cache Issues
\`\`\`bash
# Clear cache and rebuild
rm -rf node_modules dist .vite
npm install
npm run dev
\`\`\`

### 2. Development Server Won't Start

**Error:** `EADDRINUSE: address already in use`

**Solution:**
\`\`\`bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or change port in vite.config.js
server: { port: 3001 }
\`\`\`

### 3. Component Not Rendering

**Checklist:**
- [ ] Component is imported correctly
- [ ] Component is exported (default or named)
- [ ] Props are passed correctly
- [ ] No console errors
- [ ] React DevTools shows component in tree

### 4. CSS Not Loading

**Symptoms:**
- Unstyled content
- Layout broken

**Solutions:**
1. Check `import './App.css'` in main.jsx
2. Verify CSS file exists in src/
3. Clear browser cache (Ctrl+Shift+R)
4. Check for CSS syntax errors

### 5. Icons Not Showing

**Error:** `Module not found: lucide-react`

**Solution:**
\`\`\`bash
npm install lucide-react
\`\`\`

### 6. Build Fails

**Common Errors:**

#### Memory Issues
\`\`\`bash
# Increase Node memory
set NODE_OPTIONS=--max_old_space_size=4096
npm run build
\`\`\`

#### TypeScript Errors
\`\`\`bash
# If using TypeScript, check tsconfig.json
# For JavaScript, ensure no .ts/.tsx files exist
\`\`\`

### 7. Performance Issues

**Slow Loading:**
1. Enable production build: `npm run build && npm run preview`
2. Check bundle size: `npm run build -- --analyze`
3. Optimize images and assets
4. Enable code splitting in vite.config.js

**High CPU Usage:**
1. Check for infinite loops in useEffect
2. Reduce real-time updates frequency
3. Implement debouncing for rapid state changes

### 8. Audio Not Working

**Checklist:**
- [ ] Browser supports Web Audio API
- [ ] User interaction before audio starts (browser requirement)
- [ ] Audio context not suspended
- [ ] Backend API connected (if required)

## Debugging Tools

### Browser DevTools

#### Console
\`\`\`javascript
// Check for errors
console.log('Debug point reached')

// Inspect state
console.log('State:', { isPlaying, bpm, pattern })
\`\`\`

#### Network Tab
- Check API calls
- Verify resource loading
- Monitor bundle sizes

#### React DevTools
- Install React DevTools extension
- Inspect component hierarchy
- Check props and state
- Profile performance

### VS Code Debugging

Create `.vscode/launch.json`:
\`\`\`json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/src"
    }
  ]
}
\`\`\`

## Development Workflow

### Step 1: Check File Structure
\`\`\`
src/
├── components/
│   └── ui/
│       ├── button.jsx
│       ├── card.jsx
│       ├── slider.jsx
│       ├── badge.jsx
│       ├── tabs.jsx
│       └── progress.jsx
├── App.jsx
├── App.css
└── main.jsx
\`\`\`

### Step 2: Verify Imports
\`\`\`javascript
// In App.jsx, all imports should work:
import { Button } from './components/ui/button'
import { Card } from './components/ui/card'
// etc.
\`\`\`

### Step 3: Test Components Individually
Create test component:
\`\`\`jsx
function Test() {
  return <Button>Test Button</Button>
}
\`\`\`

### Step 4: Build and Deploy

#### Development
\`\`\`bash
npm run dev
# Open http://localhost:3000
\`\`\`

#### Production
\`\`\`bash
npm run build
npm run preview
# Open http://localhost:4173
\`\`\`

## Production Checklist

- [ ] All dependencies installed
- [ ] No console errors
- [ ] All features working
- [ ] Responsive design tested
- [ ] Performance optimized
- [ ] Build succeeds without errors
- [ ] Environment variables configured
- [ ] Security headers configured
- [ ] SEO meta tags added
- [ ] Analytics integrated (optional)

## Performance Optimization

### Bundle Size
\`\`\`bash
# Analyze bundle
npm run build
# Check dist/ folder size
\`\`\`

### Code Splitting
\`\`\`javascript
// Lazy load heavy components
const HeavyComponent = lazy(() => import('./HeavyComponent'))
\`\`\`

### Image Optimization
- Use WebP format
- Compress images
- Use appropriate sizes
- Lazy load images

## Security Best Practices

1. **Content Security Policy**
   - Add CSP headers in netlify.toml

2. **Environment Variables**
   - Never commit .env files
   - Use .env.example as template

3. **Dependencies**
   - Run `npm audit` regularly
   - Update dependencies: `npm update`

## Support Resources

- **Documentation**: README_PRODUCTION.md
- **React Docs**: https://react.dev
- **Vite Docs**: https://vitejs.dev
- **Issue Tracker**: GitHub Issues

## Emergency Fixes

### Complete Reset
\`\`\`bash
# Nuclear option - start fresh
rm -rf node_modules package-lock.json dist .vite
npm install
npm run dev
\`\`\`

### Rollback Changes
\`\`\`bash
git status
git checkout .
git clean -fd
\`\`\`

## Contact Support

If issues persist:
1. Check browser console for errors
2. Review this troubleshooting guide
3. Search GitHub issues
4. Create new issue with:
   - Error message
   - Steps to reproduce
   - Browser/OS info
   - Screenshots

---

**Last Updated:** October 2025
