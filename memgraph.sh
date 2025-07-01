#!/bin/bash

# Memgraph Management Script

case "$1" in
    start)
        echo "🐳 Starting Memgraph..."
        docker run -d --name memgraph -p 7687:7687 -p 7444:7444 -p 3000:3000 memgraph/memgraph-platform
        echo "✅ Memgraph started!"
        echo "📊 Memgraph Lab: http://localhost:3000"
        echo "⚠️  Warning: Data will be lost when container is removed"
        ;;
    start-persistent)
        echo "🐳 Starting Memgraph with persistent data..."
        docker run -d --name memgraph -p 7687:7687 -p 7444:7444 -p 3000:3000 \
          -v memgraph_data:/var/lib/memgraph \
          memgraph/memgraph-platform
        echo "✅ Memgraph started with persistent storage!"
        echo "📊 Memgraph Lab: http://localhost:3000"
        echo "💾 Data will be preserved across container restarts"
        ;;
    stop)
        echo "🛑 Stopping Memgraph..."
        docker stop memgraph
        docker rm memgraph
        echo "✅ Memgraph stopped!"
        ;;
    restart)
        echo "🔄 Restarting Memgraph..."
        docker stop memgraph 2>/dev/null
        docker rm memgraph 2>/dev/null
        docker run -d --name memgraph -p 7687:7687 -p 7444:7444 -p 3000:3000 memgraph/memgraph-platform
        echo "✅ Memgraph restarted!"
        echo "📊 Memgraph Lab: http://localhost:3000"
        ;;
    status)
        echo "🔍 Checking Memgraph status..."
        if docker ps | grep -q memgraph; then
            echo "✅ Memgraph is running"
            echo "📊 Memgraph Lab: http://localhost:3000"
        else
            echo "❌ Memgraph is not running"
        fi
        ;;
    logs)
        echo "📄 Showing Memgraph logs..."
        docker logs memgraph
        ;;
    *)
        echo "Usage: $0 {start|start-persistent|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start            - Start Memgraph container (data will be lost on restart)"
        echo "  start-persistent - Start Memgraph with persistent data storage"
        echo "  stop             - Stop and remove Memgraph container"
        echo "  restart          - Restart Memgraph container"
        echo "  status           - Check if Memgraph is running"
        echo "  logs             - Show Memgraph logs"
        exit 1
        ;;
esac
