"""
Template sample URLs configuration.

This module contains the mapping of template names to their sample image URLs.
Add your S3 URLs here as they become available.
"""

# Template name to S3 URL mapping
TEMPLATE_SAMPLE_URLS ={
  "education_info_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/education_info_2.png",
  "coming_soon_post_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/coming_soon_post_2.png",
  "testimonials_template_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/testimonials_template_2.png",
  "qa_template_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/qa_template_2.png",
  "event_day": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/event_day.png",
  "testimonials_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/testimonials_template.png",
  "summer_sale_promotion": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/summer_sale_promotion.png",
  "cafe_post": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/cafe_post.png",
  "quote_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/quote_template.png",
  "calendar_app_promo": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/calendar_app_promo.png",
  "product_service": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_service.png",
  "blog_post_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/blog_post_2.png",
  "product_showcase_4": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_showcase_4.png",
  "product_promotion": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_promotion.png",
  "product_showcase_3": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_showcase_3.png",
  "coming_soon_page": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/coming_soon_page.png",
  "product_showcase_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_showcase_2.png",
  "hiring_post": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/hiring_post.png",
  "product_showcase": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_showcase.png",
  "product_promotion_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_promotion_2.png",
  "product_sale": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_sale.png",
  "education_info": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/education_info.png",
  "blog_post": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/blog_post.png",
  "product_service_minimal": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_service_minimal.png",
  "qa_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/qa_template.png",
  "coming_soon": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/coming_soon.png",
  "quote_template_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/quote_template_2.png"
}

def get_sample_url(template_name: str) -> str:
    """
    Get the sample URL for a template.
    
    Args:
        template_name: Name of the template
        
    Returns:
        str: The sample URL if exists, empty string otherwise
    """
    return TEMPLATE_SAMPLE_URLS.get(template_name, "")
