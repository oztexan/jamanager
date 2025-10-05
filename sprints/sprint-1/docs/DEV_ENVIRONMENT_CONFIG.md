# Development Environment Configuration

## Dev Indicator Control

The development indicator (showing current sprint information) can be controlled through multiple methods to ensure it only appears in development environments.

### 1. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Development Settings
DEBUG=True
SHOW_DEV_INDICATOR=True
ENVIRONMENT=development
PORT=3000
```

**Environment Variables:**
- `DEBUG`: Set to `True` to enable debug mode (default: `False`)
- `SHOW_DEV_INDICATOR`: Set to `True` to show dev indicator (default: `True`)
- `ENVIRONMENT`: Set to `production` to disable dev features (default: `development`)
- `PORT`: Development port (default: `3000`)

### 2. URL Parameters

You can control the dev indicator via URL parameters:

**Hide dev indicator:**
```
http://localhost:3000/?hide-dev-indicator=true
```

**Force show dev indicator:**
```
http://localhost:3000/?show-dev-indicator=true
```

### 3. Automatic Detection

The dev indicator automatically appears when:

- **Hostname**: `localhost`, `127.0.0.1`, or `0.0.0.0`
- **Port**: `3000`, `8000`, `5000`, `3001`, or `8001`
- **Meta Tag**: `<meta name="dev-environment" content="true">` is present
- **Environment Variables**: `DEBUG=True` or `SHOW_DEV_INDICATOR=True`

### 4. Production Deployment

To deploy to production without the dev indicator:

1. **Set environment variables:**
   ```env
   DEBUG=False
   SHOW_DEV_INDICATOR=False
   ENVIRONMENT=production
   PORT=80
   ```

2. **Or use URL parameter:**
   ```
   https://yourdomain.com/?hide-dev-indicator=true
   ```

### 5. Development vs Production

| Environment | Dev Indicator | Configuration |
|-------------|---------------|---------------|
| **Development** | ✅ Shows | `DEBUG=True`, `PORT=3000` |
| **Staging** | ✅ Shows | `DEBUG=True`, `PORT=8000` |
| **Production** | ❌ Hidden | `ENVIRONMENT=production` |

### 6. Customization

The dev indicator can be customized by modifying `static/js/dev-indicator.js`:

```javascript
// Update sprint information
window.devIndicator.updateSprint(1, "Developer Experience", "Documentation ✅ | Dev Tools ✅");

// Hide the indicator
window.devIndicator.hide();

// Show the indicator
window.devIndicator.show();
```

### 7. Troubleshooting

**Dev indicator not showing:**
- Check if `DEBUG=True` in environment variables
- Verify you're on a development port (3000, 8000, etc.)
- Check browser console for JavaScript errors
- Try adding `?show-dev-indicator=true` to URL

**Dev indicator showing in production:**
- Set `ENVIRONMENT=production` in environment variables
- Set `SHOW_DEV_INDICATOR=False`
- Add `?hide-dev-indicator=true` to URL
- Verify production deployment doesn't include dev meta tags

---

**Last Updated**: 2025-10-05  
**Version**: 1.0.0
