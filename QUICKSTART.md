# 🚀 GoodFoods Quick Start Guide

## One-Minute Setup

```bash
# Step 1: Generate data
python data_generator.py

# Step 2: Test system
python test_system.py

# Step 3: Run app
streamlit run app.py
```

## API Key Setup

1. Get Groq API key: https://console.groq.com/
2. Enter in sidebar when app opens
3. Model: `llama-3.3-8b-instant`

## Example Queries

### Search
```
"Show me branches in Mumbai"
"Find GoodFoods with rooftop seating"
"What branches are in Bangalore?"
```

### Recommendations
```
"I want a romantic dinner spot"
"Find me something family-friendly with parking"
"Best branch for outdoor dining?"
```

### Booking
```
"Book a table for tomorrow at 7 PM for 4 people"
"Reserve GoodFoods Koramangala for Dec 25th, 8 PM, party of 6"
"Make a reservation in Delhi for next Friday evening"
```

## Key Files

- `app.py` - Streamlit UI
- `agent_core.py` - AI agent + tools
- `mcp_server.py` - MCP protocol
- `goodfoods_branches.json` - 51 branches data

## Documentation

- **README.md** - Full documentation
- **SUMMARY.md** - Project summary
- **use_case_document.md** - Business strategy
- **walkthrough.md** - Implementation details

## Branch Statistics

- **Total**: 51 branches
- **Cities**: 18 cities across India
- **Cuisines**: Italian, North Indian, Continental, Asian Fusion
- **Price**: ₹₹₹ (Premium, casual)
- **Hours**: 10:00 AM - 11:00 PM daily

## Features

✅ Natural language booking  
✅ Smart branch recommendations  
✅ Multi-location search  
✅ Real-time availability  
✅ Error handling & validation  
✅ 24/7 operation

## Support

- Test suite: `python test_system.py`
- Debug panel: Check "Debug: View Branch Data" in app
- Logs: Check terminal for errors

---

**Ready in < 60 seconds!** 🚀
