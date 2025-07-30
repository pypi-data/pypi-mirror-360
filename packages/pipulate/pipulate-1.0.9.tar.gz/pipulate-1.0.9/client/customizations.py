import pandas as pd
from dataclasses import dataclass, field


@dataclass
class ProjectCustomization:
    filter_function: callable = lambda df: df  # default to no-op filter


def filter_project_a(project: str, df: pd.DataFrame) -> pd.DataFrame:
    # Implement complex filter logic specific to project A
    return df[df['column'] > 10]


def mcclatchy(project: str, df: pd.DataFrame) -> pd.DataFrame:
    # Implement different logic for project B
    # First, we filter at the domain-level using project's apex domain
    domain_patterns = [
        rf'http://account\.{project}',
        rf'http://checkout\.{project}',
        rf'http://edition\.{project}',
        rf'http://eedition-gateway\.{project}',
        rf'http://hiring\.{project}',
        rf'http://jobs\.{project}',
        rf'http://learn-a-language\.{project}',
        rf'http://liveedition\.{project}',
        rf'http://media\d*\.{project}',
        rf'http://myaccount\.{project}',
        rf'http://mycheckout\.{project}',
        rf'http://subscribe\.{project}'
    ]
    
    # Next, we filter at the path level, particular about WHERE in the URL the folder is
    path_patterns = [
        '.*/home-services.*',  # Anywhere in the URL
        '.*/living/health-fitness/healthcare.*',
        '.*/product-reviews.*',
        r'^https?://[^/]+/betting.*',  # Precisely, the first folder
        r'^https?://[^/]+/cars.*',
        r'^https?://[^/]+/colaboradores.*',
        r'^https?://[^/]+/contributor-content.*',
        r'^https?://[^/]+/deals-offers.*',
        r'^https?://[^/]+/detour.*',
        r'^https?://[^/]+/family-features.*',
        r'^https?://[^/]+/finance.*',
        r'^https?://[^/]+/health-wellness.*',
        r'^https?://[^/]+/how-to-geek.*',
        r'^https?://[^/]+/learn-a-language.*',
        r'^https?://[^/]+/living/personal-finance.*',
        r'^https?://[^/]+/news/business/personal-finance.*',
        r'^https?://[^/]+/news/business/the-street.*',
        r'^https?://[^/]+/partner-videos.*',
        r'^https?://[^/]+/press-releases.*',
        r'^https?://[^/]+/product-reviews.*',
        r'^https?://[^/]+/seniors.*',
        r'^https?://[^/]+/shop-with-us.*',
        r'^https?://[^/]+/software-business.*',
        r'^https?://[^/]+/sponsored.*',
        r'^https?://[^/]+/sports/partners.*',
        r'^https?://[^/]+/sweepstakes.*'
    ]
    
    # Combine patterns with OR (|)
    combined_patterns = '|'.join(domain_patterns + path_patterns)
    df = df[~df['URL'].str.contains(combined_patterns, regex=True, case=False)]
    return df

# Dictionary to map project IDs to their specific customizations
project_customizations = {
    'fort-worth': ProjectCustomization(filter_function=mcclatchy),
    'charlotte': ProjectCustomization(filter_function=mcclatchy),
    'miami': ProjectCustomization(filter_function=mcclatchy),
    'sacramento': ProjectCustomization(filter_function=mcclatchy),
    'kansas-city': ProjectCustomization(filter_function=mcclatchy),
    'raleigh': ProjectCustomization(filter_function=mcclatchy),
}