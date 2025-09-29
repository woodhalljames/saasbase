from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from .models import BlogPost


class LatestPostsFeed(Feed):
    """RSS feed for blog posts"""
    title = "DreamWedAI Blog - Wedding Inspiration & Tips"
    link = "/blog/"
    description = "Latest wedding planning tips, trends, and real wedding stories from DreamWedAI"
    
    def items(self):
        return BlogPost.published_posts()[:20]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.excerpt
    
    def item_link(self, item):
        return item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.published_at
    
    def item_author_name(self, item):
        return item.author.get_display_name() if item.author else "DreamWedAI"
    
    def item_categories(self, item):
        categories = []
        if item.category:
            categories.append(item.category.name)
        categories.extend([tag.name for tag in item.tags.all()])
        return categories


class AtomSiteNewsFeed(LatestPostsFeed):
    """Atom feed variant"""
    feed_type = Atom1Feed
    subtitle = LatestPostsFeed.description
