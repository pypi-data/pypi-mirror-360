#!/bin/bash
#
# リンター実行スクリプト
# 使用方法: ./scripts/lint.sh [--log] [--fix]
#

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# ログディレクトリの作成
mkdir -p logs

# オプションの解析
FIX_MODE=false
LOG_MODE=false

for arg in "$@"; do
    case $arg in
        --fix)
            FIX_MODE=true
            ;;
        --log)
            LOG_MODE=true
            ;;
    esac
done

# エラーステータスを記録する変数
RUFF_ERROR=0
MYPY_ERROR=0

# Ruff実行
if [[ "$LOG_MODE" == true ]]; then
    echo "🔍 Ruff実行中..."
    if [[ "$FIX_MODE" == true ]]; then
        if ruff check src tests --fix --output-format=full > logs/ruff.log 2>&1; then
            echo "✅ Ruff チェック・修正完了"
        else
            echo "❌ Ruffでエラーが見つかりました"
            cat logs/ruff.log
            RUFF_ERROR=1
        fi
    else
        if ruff check src tests --output-format=full > logs/ruff.log 2>&1; then
            echo "✅ Ruff チェック完了"
        else
            echo "❌ Ruffでエラーが見つかりました"
            cat logs/ruff.log
            RUFF_ERROR=1
        fi
    fi

    echo "🔍 Mypy実行中..."
    if mypy src tests > logs/mypy.log 2>&1; then
        echo "✅ Mypy チェック完了"
    else
        echo "❌ Mypyでエラーが見つかりました"
        cat logs/mypy.log
        MYPY_ERROR=1
    fi

    echo "📁 ログファイル:"
    echo "  Ruff: logs/ruff.log"
    echo "  Mypy: logs/mypy.log"
else
    echo "🔍 Ruff実行中..."
    if [[ "$FIX_MODE" == true ]]; then
        if ! ruff check src tests --fix --output-format=full; then
            RUFF_ERROR=1
        fi
    else
        if ! ruff check src tests --output-format=full; then
            RUFF_ERROR=1
        fi
    fi

    echo "🔍 Mypy実行中..."
    if ! mypy src tests; then
        MYPY_ERROR=1
    fi
fi

# 最終結果の判定
if [[ $RUFF_ERROR -eq 1 || $MYPY_ERROR -eq 1 ]]; then
    echo "❌ リンターチェックでエラーが見つかりました"
    exit 1
else
    echo "✅ 全てのリンターチェックが完了しました"
fi
