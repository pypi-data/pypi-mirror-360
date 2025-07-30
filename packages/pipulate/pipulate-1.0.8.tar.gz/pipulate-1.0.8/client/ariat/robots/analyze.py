#!/usr/bin/env python
# coding: utf-8

# In[1]:

import pandas as pd
import re
from IPython.display import display, HTML, Markdown
import sys

def is_jupyter():
    """Check if running in Jupyter environment"""
    try:
        return 'ipykernel' in sys.modules
    except:
        return False

def display_section(title, content, level=2):
    """Display content with appropriate formatting based on environment"""
    if is_jupyter():
        display(HTML(f"<h{level}>{title}</h{level}>"))
        display(Markdown(content))
    else:
        print(f"\n{'='*80}\n{title}\n{'='*80}\n{content}\n")

# Define file paths (User should replace these with the actual paths if different)
gsc_file_path = '/home/mike/repos/pipulate/client/ariat/robots/all_gsc.csv'
robots_file_path = '/home/mike/repos/pipulate/client/ariat/robots/robots.csv'

# --- 1. Introduction and Overview ---
display_section("URL Parameter Analysis Report", """
This analysis examines URL parameters across your website to optimize crawling efficiency while preserving important content. 
We'll explore:
- Parameters currently receiving Google Search Console impressions
- Parameters that might be unnecessarily bloating your URLs
- Recommendations for parameter filtering in both robots.txt and JavaScript
""", level=1)

# --- 2. Read CSV files ---
try:
    gsc_df = pd.read_csv(gsc_file_path)
    robots_df = pd.read_csv(robots_file_path)
except FileNotFoundError:
    display_section("Error", "One or both CSV files were not found. Please check the file paths.")
    exit()
except Exception as e:
    display_section("Error", f"An error occurred while reading the CSV files: {e}")
    exit()

# --- 3. Extract 'Full URL' columns and convert to sets for efficient comparison ---
try:
    gsc_urls = set(gsc_df['Full URL'])
    robots_urls = set(robots_df['Full URL'])
except KeyError:
    display_section("Error", "'Full URL' column not found in one or both CSV files.")
    exit()

# --- 4. Find differing URLs ---
urls_in_gsc_not_in_robots = list(gsc_urls - robots_urls)
urls_in_robots_not_in_gsc = list(robots_urls - gsc_urls)

# --- 5. Parameter Analysis Functions ---

def analyze_query_parameters(url):
    """Analyzes a URL's query parameters against robots.txt rules."""
    if '?' not in url:
        return None
    
    # Extract query string
    query_string = url.split('?', 1)[1]
    
    # Split into parameters
    params = query_string.split('&')
    
    # Check against robots.txt rules
    blocked_by = []
    allowed_by = []
    
    # Check for too many parameters
    if len(params) > 10:
        blocked_by.append("Too many parameters (>10)")
    
    # Parameter Categories and Their Purposes
    parameter_categories = {
        'ecommerce': {
            'description': 'Parameters that affect product display, pricing, and availability',
            'patterns': ['country=', 'currency=', 'productId=', 'styleId=', 'selectedVariants=']
        },
        'tracking': {
            'description': 'Parameters used for analytics and marketing attribution',
            'patterns': ['utm_', 'gclid=', 'msclkid=', 'irclickid=']
        },
        'session': {
            'description': 'Parameters that maintain user session state',
            'patterns': ['sid=', 'session=', 'timestamp=']
        },
        'ui_ux': {
            'description': 'Parameters that control user interface elements',
            'patterns': ['format=', 'hasTemplate=', 'popup-', 'openSearch=']
        },
        'search': {
            'description': 'Parameters related to search functionality',
            'patterns': ['q=', 'gRefinements=', 'prefn1=', 'prefv1=']
        },
        'social': {
            'description': 'Parameters from social media tracking',
            'patterns': ['fbclid=', 'igshid=', 'twclid=']
        }
    }
    
    # Check against allowed parameters
    allowed_patterns = [
        'country=', 'currency=', 'utm_source=', 'bvstate=', 'gQT=',
        'gPromoCode=', 'bvroute=', 'utm_medium=', 'bc_pid=', 'utm_campaign=',
        'gRefinements=', 'source=', 'UUID=', 'msclkid=', 'utm_term=',
        'utm_content=', 'obem=', 'bc_lcid=', 'q=', 'gclid=', 'dwvar_'
    ]
    
    # Check against disallowed parameters
    disallowed_patterns = [
        'sid=', 'session=', 'timestamp=', 'random=', 'cache=',
        'dwvar_=', 'dtm_=', 'dtmc_=', 'dwfrm_=', 'dw_dnt=',
        'id=', '_=', 'value=', 'color=', 'url=', 'form=', 'filter=',
        'type=', 'data=', 'pid=', 'quantity=', 'cid=', 'vf=', 'params=',
        'title=', 'ratings=', 'swatches=', 'runningLineEnabled=', 'sw=',
        'sh=', 'recommenderName=', 'recTemplate=', 'rtbhc=', 'decimalPrice=',
        'formatted=', 'cachebuster=', 'thematic=', 'srsltid=', 'cto_pld=',
        'utm_id=', 'base_uri=', 'showProductList=', 'prefv2=', 'prefn2=',
        'pids=', 'wbraid=', 'featured_item=', 'position=', 'dwcont=',
        'sm=', 'qty=', 'amp%3Butm_medium=', 'amp%3Birgwc=', 'amp%3Butm_source=',
        'amp%3Butm_campaign=', 'ag=', 'res=', 'dwac=', 'dir=', 'cookie=',
        'fla=', 'java=', 'tz=', 'gears=', 'realp=', 'gad=', 'wma=', 'pdf=',
        'tblci=', 'kuid=', 'kref=', 'pd_influencer=', 'collage=', '_ga=',
        'hsCtaTracking=', '__hssc=', '__hsfp=', '__hstc=', 'hubs_content-cta=',
        'hubs_post-cta=', 'hubs_content=', '_mix_id=', 'rurl=', 'sfrm=',
        'gad_campaignid=', 'trk_sid=', 'trk_contact=', 'trk_msg=', 'ci=',
        'linkURL=', 'linkText=', 'fromLogOut=', 'topic=', 'openTopNav=',
        'rules=', 'defaults=', 'popup-sort=', 'at=', 'xs=', 'VO=', 'Pu=',
        'Ma=', 'jJEP=', 'CW=', 'dj=', 'w=', 'utm_x=', 'mL=', 'accTab=',
        'amp%3BisErrorMessage=', 'amp%3BpageType=', 'amp%3BisMessage=',
        'amp%3Bsh=', 'amp%3Bscid=', 'amp%3Brefid=', 'amp%3Bpid=', 'LgAj=',
        'X5=', 'src=', 'scid=', 'pcid=', 'kclt=', 'rdc=', 'uid=', 'je='
    ]
    
    for param in params:
        param = param.split('=')[0] + '='  # Get just the parameter name with =
        is_allowed = False
        is_blocked = False
        
        # Check if parameter is allowed
        for pattern in allowed_patterns:
            if param.startswith(pattern):
                allowed_by.append(param)
                is_allowed = True
                break
        
        # Check if parameter is blocked
        for pattern in disallowed_patterns:
            if param.startswith(pattern):
                blocked_by.append(param)
                is_blocked = True
                break
        
        # If not explicitly allowed or blocked, it's blocked by the catch-all rule
        if not is_allowed and not is_blocked:
            blocked_by.append(param + " (blocked by catch-all rule)")
    
    return {
        'blocked_by': blocked_by,
        'allowed_by': allowed_by,
        'total_params': len(params)
    }

def write_blocked_urls_report(blocked_urls, output_file):
    """Writes a report of blocked URLs to a file."""
    with open(output_file, 'w') as f:
        f.write("# URLs Receiving GSC Impressions But Blocked by robots.txt\n\n")
        f.write("This file contains URLs that are currently receiving Google Search Console impressions ")
        f.write("but would be blocked by the current robots.txt rules.\n\n")
        
        for url, analysis in blocked_urls:
            f.write(f"## {url}\n")
            f.write(f"- Blocked by: {', '.join(analysis['blocked_by'])}\n")
            f.write(f"- Total parameters: {analysis['total_params']}\n\n")

def analyze_parameter_frequency(mixed_urls):
    """Analyzes parameter frequency in mixed parameter URLs."""
    param_freq = {}
    for url, analysis in mixed_urls:
        for param in analysis['blocked_by']:
            param = param.split(' (')[0]  # Remove the "blocked by catch-all rule" part
            param_freq[param] = param_freq.get(param, 0) + 1
    
    # Sort by frequency
    sorted_params = sorted(param_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate breakpoints
    total_urls = len(mixed_urls)
    breakpoints = {
        'high': total_urls * 0.1,  # Top 10%
        'medium': total_urls * 0.25,  # Top 25%
        'low': total_urls * 0.5  # Top 50%
    }
    
    return sorted_params, breakpoints

def write_mixed_parameters_report(mixed_urls, output_file):
    """Writes a detailed report of mixed parameter URLs."""
    sorted_params, breakpoints = analyze_parameter_frequency(mixed_urls)
    
    with open(output_file, 'w') as f:
        f.write("# Mixed Parameter URLs Analysis\n\n")
        f.write("This report analyzes URLs that have both allowed and blocked parameters.\n\n")
        
        f.write("## Parameter Frequency Analysis\n\n")
        f.write("Parameters are categorized by their frequency of occurrence:\n\n")
        f.write("- High Frequency: Parameters appearing in >10% of URLs\n")
        f.write("- Medium Frequency: Parameters appearing in >25% of URLs\n")
        f.write("- Low Frequency: Parameters appearing in >50% of URLs\n\n")
        
        f.write("### Parameter Frequency Breakdown\n\n")
        current_category = "High Frequency"
        for param, count in sorted_params:
            if count <= breakpoints['high']:
                current_category = "Medium Frequency"
            if count <= breakpoints['medium']:
                current_category = "Low Frequency"
            if count <= breakpoints['low']:
                current_category = "Rare Parameters"
            
            f.write(f"#### {current_category}\n")
            f.write(f"- {param}: {count} occurrences ({count/len(mixed_urls)*100:.1f}% of URLs)\n\n")
        
        f.write("## Detailed URL Analysis\n\n")
        for url, analysis in mixed_urls:
            f.write(f"### {url}\n")
            f.write("#### Allowed Parameters:\n")
            for param in analysis['allowed_by']:
                f.write(f"- {param}\n")
            f.write("\n#### Blocked Parameters:\n")
            for param in analysis['blocked_by']:
                f.write(f"- {param}\n")
            f.write(f"\nTotal Parameters: {analysis['total_params']}\n\n")

def analyze_urls(url_list, description):
    """Analyzes a list of URLs and provides a summary and samples."""
    display_section(f"Analysis: {description}", f"Total URLs found: {len(url_list)}")

    if not url_list:
        print("No URLs in this category.")
        return

    # Categorize URLs
    categorized_urls = {
        "root_or_tld_like": [],
        "with_subdirectories": [],
        "with_query_parameters": [],
        "image_files": [],
        "pdf_files": [],
        "other_files": [],
        "other_patterns": []
    }

    # Track URLs that would be blocked by robots.txt
    blocked_urls = []
    allowed_urls = []
    partially_blocked_urls = []

    for url in url_list:
        try:
            path_after_domain = ""
            if '//' in url:
                path_after_domain = url.split('//', 1)[1]
                if '/' in path_after_domain:
                    path_after_domain = path_after_domain.split('/', 1)[1]
                else:
                    path_after_domain = ""

            if '?' in url:
                categorized_urls["with_query_parameters"].append(url)
                param_analysis = analyze_query_parameters(url)
                if param_analysis:
                    if param_analysis['blocked_by'] and not param_analysis['allowed_by']:
                        blocked_urls.append((url, param_analysis))
                    elif param_analysis['allowed_by'] and not param_analysis['blocked_by']:
                        allowed_urls.append((url, param_analysis))
                    elif param_analysis['allowed_by'] and param_analysis['blocked_by']:
                        partially_blocked_urls.append((url, param_analysis))
            elif re.search(r'\.(jpg|jpeg|png|gif|svg|webp)$', url, re.IGNORECASE):
                categorized_urls["image_files"].append(url)
            elif re.search(r'\.pdf$', url, re.IGNORECASE):
                categorized_urls["pdf_files"].append(url)
            elif re.search(r'\.(xml|txt|doc|docx|xls|xlsx|zip|gz|css|js)$', url, re.IGNORECASE):
                categorized_urls["other_files"].append(url)
            elif path_after_domain and '/' in path_after_domain.strip('/'):
                categorized_urls["with_subdirectories"].append(url)
            elif path_after_domain.strip('/') and not '/' in path_after_domain.strip('/'):
                 categorized_urls["root_or_tld_like"].append(url)
            elif not path_after_domain.strip('/'):
                 categorized_urls["root_or_tld_like"].append(url)
            else:
                categorized_urls["other_patterns"].append(url)
        except IndexError:
            categorized_urls["other_patterns"].append(url)

    # Print URL categorization summary
    for category, urls in categorized_urls.items():
        if urls:
            display_section(f"Category: {category.replace('_', ' ').capitalize()}", 
                          f"Found {len(urls)} URLs in this category.")
            if is_jupyter():
                display(HTML("<ul>"))
                for url in urls[:10]:
                    display(HTML(f"<li>{url}</li>"))
                if len(urls) > 10:
                    display(HTML(f"<li>... and {len(urls) - 10} more.</li>"))
                display(HTML("</ul>"))
            else:
                for url in urls[:10]:
                    print(f"    - {url}")
                if len(urls) > 10:
                    print(f"    ... and {len(urls) - 10} more.")

    # Print robots.txt analysis for URLs with query parameters
    if categorized_urls["with_query_parameters"]:
        display_section("Robots.txt Analysis for URLs with Query Parameters", f"""
        Total URLs with query parameters: {len(categorized_urls['with_query_parameters'])}
        URLs that would be blocked: {len(blocked_urls)}
        URLs that would be allowed: {len(allowed_urls)}
        URLs with mixed parameters: {len(partially_blocked_urls)}
        """)
        
        # Write reports
        if blocked_urls:
            write_blocked_urls_report(blocked_urls, '/home/mike/repos/pipulate/client/ariat/robots/blocked_urls_report.md')
            print("\n    Wrote blocked URLs report to blocked_urls_report.md")
        
        if partially_blocked_urls:
            write_mixed_parameters_report(partially_blocked_urls, '/home/mike/repos/pipulate/client/ariat/robots/mixed_parameters_report.md')
            print("\n    Wrote mixed parameters report to mixed_parameters_report.md")
            
            # Analyze parameter frequency
            sorted_params, breakpoints = analyze_parameter_frequency(partially_blocked_urls)
            display_section("Parameter Frequency Analysis", """
            High Frequency Parameters (>10% of URLs):
            """)
            for param, count in sorted_params:
                if count > breakpoints['high']:
                    print(f"      - {param}: {count} occurrences ({count/len(partially_blocked_urls)*100:.1f}% of URLs)")
                else:
                    break

def generate_robots_txt_rules():
    """Generates robots.txt rules based on parameter analysis."""
    rules = """# robots.txt for www.ariat.com
User-agent: *

# Essential E-commerce Parameters
# These parameters affect product display, pricing, and availability
Allow: /*?country=
Allow: /*?currency=
Allow: /*?productId=
Allow: /*?styleId=
Allow: /*?selectedVariants=
Allow: /*?page=
Allow: /*?prefn1=
Allow: /*?prefv1=
# Whitelisted parameter - must be preserved
Allow: /*?ratings=

# Important Tracking Parameters
# These parameters are essential for content delivery and user experience
Allow: /*?utm_source=
Allow: /*?bvstate=
Allow: /*?gQT=
Allow: /*?gPromoCode=
Allow: /*?bvroute=
Allow: /*?utm_medium=
Allow: /*?bc_pid=
Allow: /*?utm_campaign=
Allow: /*?gRefinements=
Allow: /*?source=
Allow: /*?UUID=
Allow: /*?msclkid=
Allow: /*?utm_term=
Allow: /*?utm_content=
Allow: /*?obem=
Allow: /*?bc_lcid=
Allow: /*?q=
Allow: /*?gclid=
Allow: /*?dwvar_*

# Block tracking and session parameters
# These parameters are used for analytics and don't affect content
Disallow: /*?sid=
Disallow: /*?session=
Disallow: /*?timestamp=
Disallow: /*?random=
Disallow: /*?cache=
Disallow: /*?dtm_=
Disallow: /*?dtmc_=
Disallow: /*?dwfrm_=
Disallow: /*?dw_dnt=
Disallow: /*?id=
Disallow: /*?_=
Disallow: /*?value=
Disallow: /*?url=
Disallow: /*?form=
Disallow: /*?filter=
Disallow: /*?type=
Disallow: /*?data=
Disallow: /*?quantity=
Disallow: /*?cid=
Disallow: /*?vf=
Disallow: /*?params=
Disallow: /*?swatches=
Disallow: /*?runningLineEnabled=
Disallow: /*?sw=
Disallow: /*?sh=
Disallow: /*?recommenderName=
Disallow: /*?recTemplate=
Disallow: /*?rtbhc=
Disallow: /*?decimalPrice=
Disallow: /*?formatted=
Disallow: /*?cachebuster=
Disallow: /*?thematic=
Disallow: /*?srsltid=
Disallow: /*?cto_pld=
Disallow: /*?utm_id=
Disallow: /*?base_uri=
Disallow: /*?showProductList=
Disallow: /*?prefv2=
Disallow: /*?prefn2=
Disallow: /*?pids=
Disallow: /*?wbraid=
Disallow: /*?featured_item=
Disallow: /*?position=
Disallow: /*?dwcont=
Disallow: /*?sm=
Disallow: /*?qty=
Disallow: /*?ag=
Disallow: /*?res=
Disallow: /*?dwac=
Disallow: /*?dir=
Disallow: /*?cookie=
Disallow: /*?fla=
Disallow: /*?java=
Disallow: /*?tz=
Disallow: /*?gears=
Disallow: /*?realp=
Disallow: /*?gad=
Disallow: /*?wma=
Disallow: /*?pdf=
Disallow: /*?tblci=
Disallow: /*?kuid=
Disallow: /*?kref=
Disallow: /*?pd_influencer=
Disallow: /*?collage=
Disallow: /*?_ga=
Disallow: /*?hsCtaTracking=
Disallow: /*?__hssc=
Disallow: /*?__hsfp=
Disallow: /*?__hstc=
Disallow: /*?hubs_content-cta=
Disallow: /*?hubs_post-cta=
Disallow: /*?hubs_content=
Disallow: /*?_mix_id=
Disallow: /*?rurl=
Disallow: /*?sfrm=
Disallow: /*?gad_campaignid=
Disallow: /*?trk_sid=
Disallow: /*?trk_contact=
Disallow: /*?trk_msg=
Disallow: /*?ci=
Disallow: /*?linkURL=
Disallow: /*?linkText=
Disallow: /*?fromLogOut=
Disallow: /*?topic=
Disallow: /*?openTopNav=
Disallow: /*?rules=
Disallow: /*?defaults=
Disallow: /*?popup-sort=
Disallow: /*?at=
Disallow: /*?xs=
Disallow: /*?VO=
Disallow: /*?Pu=
Disallow: /*?Ma=
Disallow: /*?jJEP=
Disallow: /*?CW=
Disallow: /*?dj=
Disallow: /*?w=
Disallow: /*?utm_x=
Disallow: /*?mL=
Disallow: /*?accTab=
Disallow: /*?LgAj=
Disallow: /*?X5=
Disallow: /*?src=
Disallow: /*?scid=
Disallow: /*?pcid=
Disallow: /*?kclt=
Disallow: /*?rdc=
Disallow: /*?uid=
Disallow: /*?je=

# Block URLs with too many parameters
# URLs with more than 10 parameters are likely tracking or session-related
Disallow: /*?*&*&*&*&*&*&*&*&*&*&*&*

# Block AJAX and popup URLs
# These are typically UI elements that don't need to be indexed
Disallow: /*?format=ajax
Disallow: /*?hasTemplate=
Disallow: /*?popup-*
Disallow: /*?openSearch=
Disallow: /*?fromPlusPLP=

# Block email tracking parameters
# These are used for email campaign tracking
Disallow: /*?qs=
Disallow: /*?irclickid=
Disallow: /*?irgwc=

# Block social media tracking
# These parameters are added by social media platforms
Disallow: /*?fbclid=
Disallow: /*?igshid=
Disallow: /*?twclid=

# Block AMP parameters
# These are automatically added by the AMP system
Disallow: /*?amp;*
"""
    return rules

def generate_pageworkers_js():
    """Generates the recommended_pageworkers.js file based on parameter analysis."""
    js_content = '''/**
 * PARAMETER BUSTER
 * ------------------------------
 * This script manages URL parameters in two ways:
 * 1. PARAMETERS_TO_REMOVE: Parameters that will be stripped from URLs
 * 2. PARAMETERS_TO_KEEP: Parameters that will NEVER be removed (whitelist)
 * 
 * Based on analysis of:
 * - URLs receiving Google Search Console impressions
 * - Mixed parameter URLs
 * - Blocked URLs report
 */

// Parameters to remove from URLs (based on analysis of blocked and mixed parameter reports)
const PARAMETERS_TO_REMOVE = [
    // Tracking parameters
    "utm_campaign", "utm_source", "utm_medium", "utm_term", "utm_content",
    "irgwc", "fbclid", "irclickid", "qs", "gclid", "msclkid",
    
    // Session and cache parameters
    "sid", "session", "timestamp", "random", "cache", "cachebuster",
    
    // UI/UX parameters
    "format", "hasTemplate", "popup-", "openSearch", "fromPlusPLP",
    
    // Analytics and tracking
    "_ga", "__hssc", "__hsfp", "__hstc", "_mix_id",
    
    // Social media tracking
    "igshid", "twclid",
    
    // Email tracking
    "trk_sid", "trk_contact", "trk_msg",
    
    // Legacy parameters
    "pid", "fdid", "swatches", "title", "runningLineEnabled",
    "recommenderName", "recTemplate"
];

// Parameters to ALWAYS keep (based on analysis of URLs receiving impressions)
const PARAMETERS_TO_KEEP = [
    // Essential e-commerce parameters
    "country", "currency", "productId", "styleId", "selectedVariants",
    "page", "prefn1", "prefv1", "ratings",  // Added ratings to whitelist
    
    // Important tracking parameters that affect content
    "bvstate", "gQT", "gPromoCode", "bvroute",
    
    // Search and navigation
    "q", "gRefinements", "source",
    
    // Product variants
    "dwvar_",
    
    // Essential UTM parameters (as they appear in URLs with impressions)
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    
    // Other important parameters
    "UUID", "bc_pid", "obem", "bc_lcid"
];

/**
 * Enhanced URL parameter cleaner
 * 
 * This function processes URLs to:
 * 1. Keep essential parameters that affect content or are important for SEO
 * 2. Remove tracking, session, and unnecessary parameters
 * 3. Handle encoded parameters and special cases
 * 4. Limit the number of parameters to prevent URL bloat
 */
function cleanupURL(url) {
    // Don't process if there's no URL or question mark
    if (!url || !url.includes('?')) return url;

    // Split URL into base and query parts
    const [baseURL, queryString] = url.split('?', 2);

    // Helper function to decode URL parameters
    function decodeParamName(paramName) {
        try {
            let decodedParam = paramName;
            let lastDecoded = '';
            while (decodedParam !== lastDecoded) {
                lastDecoded = decodedParam;
                decodedParam = decodeURIComponent(decodedParam);
            }
            return decodedParam;
        } catch (e) {
            return paramName;
        }
    }

    // Split the query string by ampersands
    const params = queryString.split('&');
    const cleanParams = [];

    for (let param of params) {
        if (!param) continue;

        const paramName = param.split('=')[0];

        // Always keep whitelisted parameters
        if (PARAMETERS_TO_KEEP.some(p => paramName === p || paramName.startsWith(p))) {
            cleanParams.push(param);
            continue;
        }

        // Remove blacklisted parameters
        if (PARAMETERS_TO_REMOVE.some(p => paramName === p || paramName.startsWith(p))) {
            continue;
        }

        // Handle encoded parameters
        if (paramName.includes('%25')) {
            const decodedParam = decodeParamName(paramName);

            // Skip heavily encoded parameters
            if (/%25{5,}/.test(paramName)) {
                continue;
            }

            // Check decoded parameter against whitelist
            if (PARAMETERS_TO_KEEP.some(p => decodedParam === p || decodedParam.startsWith(p))) {
                cleanParams.push(param);
                continue;
            }

            // Check decoded parameter against blacklist
            if (PARAMETERS_TO_REMOVE.some(p => decodedParam === p || decodedParam.startsWith(p))) {
                continue;
            }
        }

        // Keep parameters with 10 or fewer parameters
        if (params.length <= 10) {
            cleanParams.push(param);
        }
    }

    return cleanParams.length > 0 ? baseURL + '?' + cleanParams.join('&') : baseURL;
}

/**
 * Process all links in the DOM
 * 
 * This function:
 * 1. Finds all elements with href attributes
 * 2. Cleans their URLs using cleanupURL
 * 3. Updates the href if changes were made
 * 4. Marks modified elements with a data attribute
 */
function cleanupAllLinks() {
    const DOM = runtime.getDOM();
    DOM.getAllElements("[href]").forEach(function(el) {
        let originalURL = el.getAttribute("href");
        let cleanedURL = cleanupURL(originalURL);

        if (originalURL !== cleanedURL) {
            el.setAttribute("href", cleanedURL);
            el.setAttribute("data-bty-pw-id", "SO7nqKFe");
        }
    });
}

// Execute the cleanup
cleanupAllLinks();'''
    return js_content

def validate_urls_against_rules(urls, rules):
    """Validates URLs against robots.txt rules to ensure they would be allowed."""
    allowed_urls = []
    blocked_urls = []
    
    # Extract all Allow and Disallow patterns
    allow_patterns = []
    disallow_patterns = []
    
    for line in rules.split('\n'):
        line = line.strip()
        if line.startswith('Allow: '):
            allow_patterns.append(line[7:])  # Remove 'Allow: ' prefix
        elif line.startswith('Disallow: '):
            disallow_patterns.append(line[10:])  # Remove 'Disallow: ' prefix
    
    for url in urls:
        if '?' not in url:
            allowed_urls.append(url)
            continue
            
        # Extract query string
        query_string = url.split('?', 1)[1]
        params = query_string.split('&')
        
        # Check if URL has too many parameters
        if len(params) > 10:
            blocked_urls.append((url, "Too many parameters"))
            continue
            
        # Check each parameter against rules
        is_allowed = True
        blocking_reason = None
        
        for param in params:
            param = param.split('=')[0] + '='
            
            # Check if parameter is explicitly allowed
            param_allowed = False
            for pattern in allow_patterns:
                if pattern.endswith('=') and param == pattern:
                    param_allowed = True
                    break
                elif pattern.endswith('*') and param.startswith(pattern[:-1]):
                    param_allowed = True
                    break
            
            # Check if parameter is explicitly blocked
            param_blocked = False
            for pattern in disallow_patterns:
                if pattern.endswith('=') and param == pattern:
                    param_blocked = True
                    blocking_reason = f"Parameter blocked: {param}"
                    break
                elif pattern.endswith('*') and param.startswith(pattern[:-1]):
                    param_blocked = True
                    blocking_reason = f"Parameter blocked: {param}"
                    break
            
            if param_blocked:
                is_allowed = False
                break
        
        if is_allowed:
            allowed_urls.append(url)
        else:
            blocked_urls.append((url, blocking_reason))
    
    return allowed_urls, blocked_urls

# Write robots.txt rules to file
with open('/home/mike/repos/pipulate/client/ariat/robots/recommend_robots.txt', 'w') as f:
    f.write(generate_robots_txt_rules())

# Write pageworkers.js to file
with open('/home/mike/repos/pipulate/client/ariat/robots/recommended_pageworkers.js', 'w') as f:
    f.write(generate_pageworkers_js())

# --- 6. Output the results ---
display_section("URL Analysis Results", """
This analysis compares URLs between your Google Search Console data and robots.csv file to identify:
1. URLs receiving impressions but not in robots.csv
2. URLs in robots.csv but not receiving impressions
3. Parameter patterns that affect crawling and indexing
""")

analyze_urls(urls_in_gsc_not_in_robots, "URLs in all_gsc.csv but NOT in robots.csv")
print("\n" + "="*50 + "\n")
analyze_urls(urls_in_robots_not_in_gsc, "URLs in robots.csv but NOT in all_gsc.csv")

display_section("Summary of Differences", f"""
Number of URLs unique to 'all_gsc.csv': {len(urls_in_gsc_not_in_robots)}
Number of URLs unique to 'robots.csv': {len(urls_in_robots_not_in_gsc)}
""")

display_section("Interpretation Guidance", """
### URLs in 'all_gsc.csv' but not 'robots.csv':
These are URLs that Google Search Console has data for (impressions, clicks, etc.),
but they are not listed in your 'robots.csv' (which typically lists URLs and their indexability).
This could mean:
* These URLs are indexable and receiving traffic, but perhaps you haven't explicitly tracked their indexability status in 'robots.csv'.
* There might be variations (e.g., HTTP vs HTTPS, www vs non-www, trailing slashes) that cause them to appear different.
* They were previously in 'robots.csv' but have been removed.

### URLs in 'robots.csv' but not 'all_gsc.csv':
These are URLs listed in your 'robots.csv', but Google Search Console has no (or negligible) data for them.
This could mean:
* These URLs are not being indexed or are not receiving impressions/clicks (perhaps they are new, blocked by robots.txt, noindexed, canonicalized to other URLs, or simply not ranking).
* The 'Is Indexable' status in 'robots.csv' might be 'False' for many of these.
* They are very low-traffic pages.
* There might be discrepancies in URL formatting between the two files.

Note: The URL categorization is a basic heuristic. Review the samples to understand the nature of the differing URLs.
""")

# After generating the robots.txt rules, validate the URLs
rules = generate_robots_txt_rules()
allowed_urls, blocked_urls = validate_urls_against_rules(gsc_urls, rules)

display_section("URL Validation Results", f"""
Total URLs in all_gsc.csv: {len(gsc_urls)}
URLs that would be allowed: {len(allowed_urls)} ({len(allowed_urls)/len(gsc_urls)*100:.1f}%)
URLs that would be blocked: {len(blocked_urls)} ({len(blocked_urls)/len(gsc_urls)*100:.1f}%)

Blocked URLs (first 10):
""")

if blocked_urls:
    for url, reason in blocked_urls[:10]:
        print(f"- {url}")
        print(f"  Reason: {reason}")
    if len(blocked_urls) > 10:
        print(f"... and {len(blocked_urls) - 10} more blocked URLs")

# Write validation results to a file
with open('/home/mike/repos/pipulate/client/ariat/robots/validation_report.md', 'w') as f:
    f.write("# URL Validation Report\n\n")
    f.write("This report shows which URLs from all_gsc.csv would be allowed or blocked by the recommended robots.txt rules.\n\n")
    
    f.write(f"## Summary\n\n")
    f.write(f"- Total URLs analyzed: {len(gsc_urls)}\n")
    f.write(f"- URLs that would be allowed: {len(allowed_urls)} ({len(allowed_urls)/len(gsc_urls)*100:.1f}%)\n")
    f.write(f"- URLs that would be blocked: {len(blocked_urls)} ({len(blocked_urls)/len(gsc_urls)*100:.1f}%)\n\n")
    
    if blocked_urls:
        f.write("## Blocked URLs\n\n")
        for url, reason in blocked_urls:
            f.write(f"### {url}\n")
            f.write(f"Reason: {reason}\n\n")

# In[ ]:

# Note: This file was converted from a Jupyter notebook to a Python script
# while maintaining the notebook cell structure. The output is not preserved
# in this format, but the code remains executable.

