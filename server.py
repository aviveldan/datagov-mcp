# server.py
from fastmcp import FastMCP, Context
from mcp.types import PromptMessage, TextContent
import requests

# Create an MCP server
mcp = FastMCP("DataGovIL", dependencies=["requests"])

# Base URL for the API
BASE_URL = "https://data.gov.il/api/3"


@mcp.prompt()
async def discover_datasets(ctx: Context, topic: str, organization: str = "") -> list[PromptMessage]:
    """Guide users through discovering relevant datasets on data.gov.il based on their topic of interest.
    
    Args:
        topic: The main topic or domain of interest (e.g., "education", "health", "transportation")
        organization: Optional specific organization to focus on (e.g., "משרד החינוך", "משרד הבריאות")
    """
    await ctx.info(f"Creating dataset discovery guide for topic: {topic}")
    
    prompt_content = f"""I need to help you discover relevant datasets about "{topic}" from the Israeli government data portal (data.gov.il).

Here's a structured approach to find the most relevant datasets:

## Step 1: Start with a broad search
Use the `package_search` tool with these parameters:
- q: "{topic}" (your main topic)
- rows: 20 (get more results to explore)
- sort: "score desc" (most relevant first)

## Step 2: Explore organizations (if not specified)
{f'Focus on organization: "{organization}"' if organization else '''Use `organization_list` to see all available organizations, then use `organization_show` to explore organizations that might have relevant data for your topic.'''}

## Step 3: Refine your search
Based on initial results, refine your search with:
- More specific keywords related to {topic}
- Filter by organization using fq parameter: "organization:{organization}" {f'(focus on {organization})' if organization else ''}
- Filter by resource format if you need specific data types

## Step 4: Examine promising datasets
For each relevant dataset found:
1. Use `package_show` to get detailed metadata
2. Check the resources available and their formats
3. Use `datastore_search` to preview the actual data structure

## Step 5: Extract the data
Once you've identified the right dataset:
- Use `fetch_data` with the dataset name for quick access
- Or use `datastore_search` for more control over the query

## Common Israeli Government Topics and Keywords:
- Education (חינוך): schools, students, teachers, universities, מוסדות חינוך
- Health (בריאות): hospitals, clinics, medical services, בתי חולים
- Transportation (תחבורה): public transport, traffic, roads, תחבורה ציבורית
- Environment (סביבה): air quality, water, waste, איכות אוויר
- Economics (כלכלה): budget, spending, taxes, תקציב
- Demographics (דמוגרפיה): population, census, statistics, אוכלוסיה

Let's start by searching for datasets related to "{topic}". What would you like to focus on first?"""

    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt_content)
        )
    ]


def _get_analysis_guidance(goal: str) -> str:
    """Helper function to provide specific guidance based on analysis goal."""
    guidance_map = {
        "trend analysis": """
   - Look for date/time fields in the data
   - Sort by date to see chronological patterns
   - Use different time ranges with offset and limit
   - Compare recent vs historical data""",
        
        "comparison": """
   - Identify categorical fields for comparison (region, type, organization)
   - Use filters (q parameter) to get specific subsets
   - Look for numeric fields that can be compared across categories
   - Extract data for different groups separately""",
        
        "general exploration": """
   - Start with broad queries to understand the data scope
   - Examine all available fields and their typical values
   - Look for relationships between different fields
   - Identify the most interesting or useful data points""",
        
        "statistical analysis": """
   - Focus on numeric fields suitable for statistics
   - Get larger samples (limit: 1000+) for meaningful analysis
   - Look for fields that can be aggregated or calculated
   - Check for completeness and data quality issues"""
    }
    
    return guidance_map.get(goal.lower(), guidance_map["general exploration"])


@mcp.prompt()
async def analyze_dataset_workflow(ctx: Context, dataset_id: str, analysis_goal: str = "general exploration") -> list[PromptMessage]:
    """Guide users through a comprehensive workflow for analyzing a specific dataset from data.gov.il.
    
    Args:
        dataset_id: The ID or name of the dataset to analyze
        analysis_goal: What the user wants to achieve (e.g., "trend analysis", "comparison", "general exploration")
    """
    await ctx.info(f"Creating analysis workflow for dataset: {dataset_id}")
    
    prompt_content = f"""I'll guide you through a comprehensive analysis of the dataset "{dataset_id}" with a focus on {analysis_goal}.

## Step-by-Step Analysis Workflow:

### Phase 1: Dataset Understanding
1. **Get Dataset Metadata**
   ```
   Use `package_show` with id: "{dataset_id}"
   ```
   - Review the title, description, and tags
   - Check the organization that published it
   - Note the last update date and frequency
   - Examine available resources and formats

2. **Preview the Data Structure**
   ```
   Use `datastore_search` with resource_id from the first resource
   Set limit: 5 to get a quick preview
   ```
   - Understand the columns/fields available
   - Check data types and formats
   - Identify key fields for your analysis

### Phase 2: Data Exploration
3. **Get Sample Data**
   ```
   Use `fetch_data` with dataset_name: "{dataset_id}" and limit: 100
   ```
   - Examine the actual data values
   - Look for patterns, missing values, or anomalies
   - Understand the data quality and completeness

4. **Explore Data Range and Distribution**
   ```
   Use `datastore_search` with different parameters:
   - Sort by different fields to see value ranges
   - Use offset to sample different parts of the dataset
   - Set fields parameter to focus on specific columns
   ```

### Phase 3: Targeted Analysis (Based on your goal: {analysis_goal})
{_get_analysis_guidance(analysis_goal)}

### Phase 4: Data Extraction for Further Analysis
5. **Extract Relevant Data**
   ```
   Use `datastore_search` with optimized parameters:
   - Set appropriate limit (1000+ for statistical analysis)
   - Use sort parameter to order by relevant fields
   - Filter with q parameter if you need specific subsets
   - Use fields parameter to get only needed columns
   ```

### Tips for Effective Analysis:
- **Hebrew Content**: Many datasets contain Hebrew text - be prepared for RTL content
- **Date Formats**: Israeli datasets often use DD/MM/YYYY format
- **Government Structure**: Understand Israeli ministry names and administrative divisions
- **Data Updates**: Check update frequency - some datasets are updated monthly/yearly
- **Completeness**: Government datasets may have missing periods during holidays or transitions

### Common Analysis Patterns:
- **Time Series**: Look for date fields to analyze trends over time
- **Geographic**: Many datasets include city/region for spatial analysis  
- **Categorical**: Government data often categorized by ministry, type, status
- **Comparative**: Compare across regions, time periods, or categories

Let's start with getting the metadata for "{dataset_id}". What specific aspect of {analysis_goal} interests you most?"""

    return [
        PromptMessage(
            role="user", 
            content=TextContent(type="text", text=prompt_content)
        )
    ]


def _get_search_strategy(objective: str) -> str:
    """Helper function to provide specific search strategies based on objective."""
    strategies = {
        "specific dataset": """
- Use exact dataset names or unique identifiers in quotes
- Try variations of the dataset name in Hebrew and English
- Filter by the organization if you know it
- Use res_format filter if you need specific file types
- Check both title and description fields""",
        
        "topic exploration": """
- Start with broad topic keywords  
- Use tag exploration to find related datasets
- Filter by multiple organizations working in the topic area
- Sort by relevance first, then by update date
- Use wildcard searches (topic*) to catch variations""",
        
        "recent data": """
- Sort by "metadata_modified desc" to get newest first
- Filter by last modification date using date ranges
- Focus on organizations known for regular updates
- Look for datasets with "real-time" or "daily" tags
- Check update frequency in dataset descriptions""",
        
        "api data": """
- Search for "API" in titles and descriptions
- Filter by res_format:"API" or tags:"API"
- Look for datasets with multiple resource formats
- Check for documentation resources (PDF, HTML)
- Focus on technical/developer-oriented descriptions""",
        
        "general": """
- Use broad, relevant keywords
- Explore different sorting options
- Check organization diversity in results
- Look for high-quality, well-documented datasets
- Balance between recent and comprehensive data"""
    }
    
    return strategies.get(objective.lower(), strategies["general"])


@mcp.prompt()
async def explore_organization_data(ctx: Context, organization_name: str = "") -> list[PromptMessage]:
    """Guide users through exploring all datasets available from a specific Israeli government organization.
    
    Args:
        organization_name: Name of the organization to explore (in Hebrew or English)
    """
    await ctx.info(f"Creating organization exploration guide for: {organization_name}")
    
    org_guidance = f"""for "{organization_name}" """ if organization_name else ""
    
    prompt_content = f"""I'll help you explore all available datasets {org_guidance}from Israeli government organizations on data.gov.il.

## Organization Data Exploration Workflow:

### Step 1: Discover Organizations
{f'You specified: "{organization_name}"' if organization_name else '''First, let's see what organizations are available:
```
Use `organization_list` to get all organizations
```'''}

### Step 2: Get Organization Details
```
Use `organization_show` with id: "{organization_name if organization_name else '[organization_id]'}"
```
This will show:
- Official organization name (Hebrew/English)
- Description and purpose
- Number of datasets published
- Organization metadata

### Step 3: Find Organization's Datasets
```
Use `package_search` with:
- fq: "organization:{organization_name if organization_name else '[organization_name]'}"
- rows: 50 (get comprehensive results)
- sort: "metadata_modified desc" (most recently updated first)
```

### Step 4: Categorize the Datasets
Organize findings by:
- **Data Types**: Statistical, operational, research, regulatory
- **Update Frequency**: Real-time, daily, monthly, yearly, one-time
- **Topics**: Core functions of the organization
- **Formats**: CSV, JSON, Excel, PDF, APIs

### Step 5: Identify High-Value Datasets
Look for datasets that are:
- Recently updated (active maintenance)
- Well-documented (good metadata)
- Machine-readable formats (CSV, JSON)
- Comprehensive coverage

## Major Israeli Government Organizations:

### Core Ministries:
- **משרד החינוך** (Ministry of Education): Schools, students, teachers, educational statistics
- **משרד הבריאות** (Ministry of Health): Hospitals, health services, medical statistics
- **משרד התחבורה** (Ministry of Transportation): Public transport, traffic, infrastructure
- **משרד הפנים** (Ministry of Interior): Population, municipalities, local government
- **משרד האוצר** (Ministry of Finance): Budget, spending, economic data

### Data-Rich Organizations:
- **הלשכה המרכזית לסטטיסטיקה** (Central Bureau of Statistics): Demographics, economics, social data
- **רשות המסים** (Tax Authority): Business registrations, tax statistics
- **בנק ישראל** (Bank of Israel): Financial and economic indicators
- **משרד הכלכלה והתעשייה** (Ministry of Economy): Business, industry, trade data
- **רשות החברות הממשלתיות** (Government Companies Authority): Public company data

### Municipal Data:
- **עיריית תל אביב** (Tel Aviv Municipality): Urban data, services, transportation
- **עיריית ירושלים** (Jerusalem Municipality): City services, development, tourism
- **Other municipalities**: Local services, planning, demographics

Let's start by exploring the organization{f' "{organization_name}"' if organization_name else 's available'}. What type of data are you most interested in from this organization?"""

    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt_content)
        )
    ]


@mcp.prompt()
async def search_optimization_guide(ctx: Context, search_objective: str = "general") -> list[PromptMessage]:
    """Guide users on how to create effective search queries for Israeli government data.
    
    Args:
        search_objective: Type of search (e.g., "specific dataset", "topic exploration", "recent data", "api data")
    """
    await ctx.info(f"Creating search optimization guide for: {search_objective}")
    
    prompt_content = f"""I'll help you optimize your searches on data.gov.il to find exactly what you need for: {search_objective}.

## Search Strategy Guide:

### Understanding data.gov.il Search:
The Israeli government data portal uses CKAN search, which supports:
- **Full-text search**: Searches titles, descriptions, tags, and content
- **Field filtering**: Target specific metadata fields
- **Boolean operators**: AND, OR, NOT for complex queries
- **Phrase matching**: Use quotes for exact phrases
- **Wildcards**: Use * for partial matching

### Optimized Search Parameters:

#### For `package_search`:
```
Basic Search:
- q: "your search terms" (main query)
- rows: 20-50 (more results for exploration, fewer for specific needs)
- start: 0 (pagination offset)

Advanced Filtering:
- fq: "field:value" (filter by specific fields)
  * organization:"ministry_name" 
  * tags:"topic_tag"
  * res_format:"CSV" or "JSON" or "Excel"
  * type:"dataset"

Sorting Options:
- sort: "score desc" (relevance - default)
- sort: "metadata_modified desc" (newest first)  
- sort: "name asc" (alphabetical)
- sort: "title_string asc" (by title)
```

### Search Techniques by Objective:

#### {search_objective.title()} Search Strategy:
{_get_search_strategy(search_objective)}

### Hebrew and English Search Tips:

#### Language Strategies:
1. **Bilingual Keywords**: Try both Hebrew and English terms
   - חינוך / education
   - בריאות / health  
   - תחבורה / transportation
   - סביבה / environment

2. **Organization Names**: Use official Hebrew names
   - משרד החינוך (not "education ministry")
   - משרד הבריאות (not "health ministry")

3. **Common Terms**:
   - נתונים / data
   - סטטיסטיקה / statistics  
   - מידע / information
   - דוח / report

### Filter Combinations for Better Results:

#### High-Quality Data:
```fq: "res_format:(CSV OR JSON) AND organization:ministry*"```

#### Recent Updates:
```fq: "metadata_modified:[2023-01-01T00:00:00Z TO *]"```

#### Specific Data Types:
```fq: "tags:(API OR real-time OR statistics)"```

### Resource-Level Search:
Use `resource_search` for finding specific files:
```
query: "your terms"
order_by: "last_modified desc"
limit: 50
```

### Pro Tips:
- **Start broad, then narrow**: Begin with general terms, then add filters
- **Check tags**: Successful searches often reveal useful tags for further filtering
- **Explore organizations**: Good datasets often come from the same organizations
- **Update recency**: Prefer recently updated datasets for current data
- **Format preference**: CSV and JSON are usually better for analysis than PDF
- **API availability**: Look for datasets with API access for dynamic data

Let's optimize your search for {search_objective}. What specific information are you looking for?"""

    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt_content)
        )
    ]


@mcp.tool()
async def status_show(ctx: Context):
    """Get the CKAN version and a list of installed extensions."""
    await ctx.info("Fetching CKAN status...")
    response = requests.post(f"{BASE_URL}/action/status_show")
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def license_list(ctx: Context):
    """Get the list of licenses available for datasets on the site."""
    await ctx.info("Fetching license list...")
    response = requests.get(f"{BASE_URL}/action/license_list")
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def package_list(ctx: Context):
    """Get a list of all package IDs (datasets)."""
    await ctx.info("Fetching package list...")
    response = requests.get(f"{BASE_URL}/action/package_list")
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def package_search(ctx: Context, q: str = "", fq: str = "",
                         sort: str = "", rows: int = 20, start: int = 0,
                         include_private: bool = False):

    """Find packages (datasets) matching query terms."""
    await ctx.info("Searching for packages...")
    params = {
        "q": q,
        "fq": fq,
        "sort": sort,
        "rows": rows,
        "start": start,
        "include_private": include_private
    }
    response = requests.get(f"{BASE_URL}/action/package_search", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def package_show(ctx: Context, id: str):
    """Get metadata about one specific package (dataset)."""
    await ctx.info(f"Fetching metadata for package: {id}")
    params = {"id": id}
    response = requests.get(f"{BASE_URL}/action/package_show", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def organization_list(ctx: Context):
    """Get names of all organizations."""
    await ctx.info("Fetching organization list...")
    response = requests.get(f"{BASE_URL}/action/organization_list")
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def organization_show(ctx: Context, id: str):
    """Get details of a specific organization."""
    await ctx.info(f"Fetching details for organization: {id}")
    params = {"id": id}
    response = requests.get(f"{BASE_URL}/action/organization_show",
                            params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def resource_search(ctx: Context, query: str = "", order_by: str = "",
                          offset: int = 0, limit: int = 100):
    """Find resources based on their field values."""
    await ctx.info("Searching for resources...")
    params = {
        "query": query,
        "order_by": order_by,
        "offset": offset,
        "limit": limit
    }
    response = requests.get(f"{BASE_URL}/action/resource_search", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def datastore_search(ctx: Context, resource_id: str, q: str = "",
                           distinct: bool = False, plain: bool = True,
                           limit: int = 100, offset: int = 0, fields: str = "",
                           sort: str = "", include_total: bool = True,
                           records_format: str = "objects"):
    """Search a datastore resource."""
    await ctx.info(f"Searching datastore for resource: {resource_id}")
    params = {
        "resource_id": resource_id,
        "q": q,
        "distinct": distinct,
        "plain": plain,
        "limit": limit,
        "offset": offset,
        "fields": fields,
        "sort": sort,
        "include_total": include_total,
        "records_format": records_format
    }
    response = requests.get(f"{BASE_URL}/action/datastore_search", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def fetch_data(dataset_name: str, limit: int = 100, offset: int = 0):
    """Fetch data from public API based on a dataset name query"""
    def find_resource_id(dataset_name):
        dataset_url = f"{BASE_URL}/action/package_show?id={dataset_name}"
        response = requests.get(dataset_url)
        if response.status_code == 200:
            dataset_data = response.json()
            resources = dataset_data['result']['resources']
            if resources:
                return resources[0]['id']
        return None

    resource_id = find_resource_id(dataset_name)
    if not resource_id:
        return {"error": f"No dataset found matching '{dataset_name}'"}

    base_url = f"{BASE_URL}/action/datastore_search"
    params = {
        "resource_id": resource_id,
        "limit": limit,
        "offset": offset
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    api_data = response.json()

    if api_data.get("success"):
        return api_data["result"]["records"]
    else:
        raise Exception(api_data.get("error", "Unknown error occurred"))


if __name__ == "__main__":
    # This code only runs when the file is executed directly
    mcp.run()
