#!/bin/bash

# Performance Validation Hook
# Ensures performance and scalability best practices

echo "⚡ Validating Performance & Scalability..."

ERRORS=0

# Check for database indexing
echo "Checking database optimization..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for index definitions in models
    INDEX_PATTERNS="Index\(|index=True|db_index=True"
    if find backend -name "*.py" -exec grep -l -E "$INDEX_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Database indexes found"
    else
        echo "⚠️  No database indexes found - consider adding indexes for frequently queried fields"
    fi

    # Check for pagination implementation
    PAGINATION_PATTERNS="limit\(|offset\(|skip\(|take\("
    if find backend -name "*.py" -exec grep -l -E "$PAGINATION_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Pagination implementation found"
    else
        echo "⚠️  No pagination found - all data lists should be paginated"
    fi

    # Check for N+1 query patterns (potential issues)
    N1_PATTERNS="for.*in.*query|\.all\(\).*for"
    if find backend -name "*.py" -exec grep -l -E "$N1_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "⚠️  Potential N+1 query patterns found - review for optimization:"
        find backend -name "*.py" -exec grep -H -E "$N1_PATTERNS" {} \; 2>/dev/null | head -3
    fi

    # Check for eager loading (solution to N+1)
    EAGER_LOADING="joinedload|selectinload|subqueryload"
    if find backend -name "*.py" -exec grep -l -E "$EAGER_LOADING" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Eager loading patterns found"
    fi

    # Check for bulk operations
    BULK_PATTERNS="bulk_insert|bulk_update|bulk_save"
    if find backend -name "*.py" -exec grep -l -E "$BULK_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Bulk operations found"
    fi
fi

# Check for Gemini Context Caching
echo "Checking Gemini optimization..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for context caching implementation
    CONTEXT_CACHE_PATTERNS="context.*cache|cached_content|ttl.*hour"
    if find backend -name "*.py" -exec grep -l -E "$CONTEXT_CACHE_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Gemini Context Caching implementation found"
    else
        echo "❌ Gemini Context Caching not found - required for performance"
        ERRORS=$((ERRORS + 1))
    fi

    # Check for rate limiting on Gemini calls
    RATE_LIMIT_PATTERNS="rate_limit|throttle|sleep\(|time\.sleep"
    if find backend -name "*.py" -exec grep -l -E "$RATE_LIMIT_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Rate limiting implementation found"
    else
        echo "❌ Rate limiting not found - required for Gemini API calls"
        ERRORS=$((ERRORS + 1))
    fi

    # Check for structured output usage
    STRUCTURED_OUTPUT="response_mime_type.*json|GenerationConfig.*response_mime_type"
    if find backend -name "*.py" -exec grep -l -E "$STRUCTURED_OUTPUT" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Structured output implementation found"
    else
        echo "⚠️  Structured output not found - ensure JSON responses from Gemini"
    fi

    # Check for separate API calls strategy
    SEPARATE_CALLS="def.*generate_|def.*chat_|def.*analyze_"
    if find backend -name "*.py" -exec grep -l -E "$SEPARATE_CALLS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Separate API call functions found"
    fi
fi

# Check for performance monitoring
echo "Checking performance monitoring..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for logging implementation
    LOGGING_PATTERNS="import logging|logger\.|log\."
    if find backend -name "*.py" -exec grep -l -E "$LOGGING_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Logging implementation found"
    else
        echo "❌ No logging found - required for performance monitoring"
        ERRORS=$((ERRORS + 1))
    fi

    # Check for performance metrics
    METRICS_PATTERNS="time\.|datetime\.|performance|metrics"
    if find backend -name "*.py" -exec grep -l -E "$METRICS_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Performance metrics patterns found"
    fi

    # Check for async/await usage for better performance
    ASYNC_PATTERNS="async def|await "
    if find backend -name "*.py" -exec grep -l -E "$ASYNC_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Async/await patterns found"
    else
        echo "⚠️  No async patterns found - consider async for I/O operations"
    fi
fi

# Check for caching strategies
echo "Checking caching implementation..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for caching libraries (but not Redis as per spec)
    CACHE_PATTERNS="@cache|@lru_cache|functools.*cache"
    if find backend -name "*.py" -exec grep -l -E "$CACHE_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Caching implementation found"
    else
        echo "⚠️  No caching found - consider caching for frequent operations"
    fi

    # Check for Redis usage (should not be used per spec)
    REDIS_PATTERNS="import redis|from redis"
    if find backend -name "*.py" -exec grep -l -E "$REDIS_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ Redis usage found - spec requires only Gemini Context Cache"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check frontend performance
echo "Checking frontend performance..."

if find frontend -name "*.js" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for excessive DOM queries
    DOM_QUERIES="document\.querySelector|document\.getElementById"
    DOM_COUNT=$(find frontend -name "*.js" -exec grep -o -E "$DOM_QUERIES" {} \; 2>/dev/null | wc -l)
    if [ "$DOM_COUNT" -gt 20 ]; then
        echo "⚠️  High number of DOM queries ($DOM_COUNT) - consider caching DOM elements"
    else
        echo "✅ DOM query usage appears reasonable"
    fi

    # Check for event delegation vs multiple listeners
    EVENT_LISTENERS="addEventListener"
    EVENT_COUNT=$(find frontend -name "*.js" -exec grep -o -E "$EVENT_LISTENERS" {} \; 2>/dev/null | wc -l)
    if [ "$EVENT_COUNT" -gt 15 ]; then
        echo "⚠️  High number of event listeners ($EVENT_COUNT) - consider event delegation"
    else
        echo "✅ Event listener usage appears reasonable"
    fi

    # Check for debouncing/throttling
    OPTIMIZATION_PATTERNS="debounce|throttle|setTimeout.*function"
    if find frontend -name "*.js" -exec grep -l -E "$OPTIMIZATION_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Performance optimization patterns found"
    fi
fi

# Check for Bootstrap optimization
echo "Checking Bootstrap usage..."

if find frontend -name "*.html" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for Bootstrap CDN vs local (CDN is faster)
    if find frontend -name "*.html" -exec grep -l "bootstrap.*cdn" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Bootstrap CDN usage found (better performance)"
    elif find frontend -name "*.html" -exec grep -l "bootstrap" {} \; 2>/dev/null | grep -q .; then
        echo "⚠️  Local Bootstrap found - consider CDN for better performance"
    fi

    # Check for custom CSS that might conflict with Bootstrap
    CUSTOM_CSS_COUNT=$(find frontend -name "*.css" -type f 2>/dev/null | wc -l)
    if [ "$CUSTOM_CSS_COUNT" -gt 3 ]; then
        echo "⚠️  Multiple custom CSS files ($CUSTOM_CSS_COUNT) - ensure efficient loading"
    fi
fi

# Check for database connection optimization
echo "Checking database connection..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for connection pooling
    POOL_PATTERNS="pool_size|max_overflow|poolclass"
    if find backend -name "*.py" -exec grep -l -E "$POOL_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Database connection pooling found"
    else
        echo "⚠️  No connection pooling found - consider for production"
    fi

    # Check for connection management
    CONN_PATTERNS="session.*close|with.*session|sessionmaker"
    if find backend -name "*.py" -exec grep -l -E "$CONN_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Proper session management found"
    fi
fi

if [ $ERRORS -eq 0 ]; then
    echo "✅ Performance validation passed"
    exit 0
else
    echo "❌ Performance validation failed with $ERRORS errors"
    echo "Performance issues found! Address these for optimal application performance."
    exit 1
fi