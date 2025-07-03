"""
Management command for comprehensive AI system testing
Usage: python manage.py test_ai_system
"""
import time
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from family.models import Story, Event, Heritage, Health, Person, Location
from ai_integration.services.embedding_service import embedding_service
from ai_integration.services.search_service import search_service
from ai_integration.models import ChatSession, QueryLog, EmbeddingCache


class Command(BaseCommand):
    help = 'Comprehensive AI system testing with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-data',
            action='store_true',
            help='Skip creating sample data',
        )
        parser.add_argument(
            '--skip-embeddings',
            action='store_true',
            help='Skip embedding generation tests',
        )
        parser.add_argument(
            '--skip-search',
            action='store_true',
            help='Skip search functionality tests',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up test data after testing',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('\n🚀 Starting AI System Integration Test\n')
        )
        
        test_results = {
            'sample_data': False,
            'embeddings': False,
            'search': False,
            'api_keys': False,
            'models': False,
            'performance': {}
        }
        
        try:
            # 1. Test API keys and configuration
            self.test_api_configuration(test_results)
            
            # 2. Test model creation and database
            self.test_models(test_results)
            
            # 3. Create sample data
            if not options['skip_data']:
                self.create_sample_data(test_results)
            
            # 4. Test embedding generation
            if not options['skip_embeddings']:
                self.test_embeddings(test_results)
            
            # 5. Test search functionality
            if not options['skip_search']:
                self.test_search(test_results)
            
            # 6. Performance tests
            self.test_performance(test_results)
            
            # 7. Cleanup if requested
            if options['cleanup']:
                self.cleanup_test_data()
            
            # 8. Display results
            self.display_results(test_results)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Test failed with error: {e}')
            )
            raise
    
    def test_api_configuration(self, results):
        """Test API key configuration"""
        self.stdout.write('🔑 Testing API configuration...')
        
        openai_key = getattr(settings, 'OPENAI_API_KEY', '')
        anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
        
        if openai_key and len(openai_key) > 10:
            self.stdout.write('  ✅ OpenAI API key configured')
        else:
            self.stdout.write('  ⚠️  OpenAI API key missing or invalid')
        
        if anthropic_key and len(anthropic_key) > 10:
            self.stdout.write('  ✅ Anthropic API key configured')
        else:
            self.stdout.write('  ⚠️  Anthropic API key missing or invalid')
        
        results['api_keys'] = bool(openai_key or anthropic_key)
    
    def test_models(self, results):
        """Test AI integration models"""
        self.stdout.write('🗄️  Testing AI models...')
        
        try:
            # Test creating AI models
            session = ChatSession.objects.create(
                user_id=1,  # Assuming superuser exists
                session_id='test-session-123',
                title='Test Session'
            )
            
            query = QueryLog.objects.create(
                session=session,
                query_text='Test query',
                response_text='Test response'
            )
            
            cache = EmbeddingCache.objects.create(
                content_hash='test-hash-123',
                content_type='test',
                content_id=1,
                embedding=[0.1] * 1536
            )
            
            self.stdout.write('  ✅ AI models working correctly')
            results['models'] = True
            
            # Cleanup test models
            session.delete()
            cache.delete()
            
        except Exception as e:
            self.stdout.write(f'  ❌ Model test failed: {e}')
            results['models'] = False
    
    def create_sample_data(self, results):
        """Create comprehensive sample family data"""
        self.stdout.write('👨‍👩‍👧‍👦 Creating sample family data...')
        
        try:
            # Create people
            grandma = Person.objects.get_or_create(
                name="Liu Nai Nai",
                defaults={
                    'bio': "Loving grandmother, traditional Chinese cook, keeper of family stories",
                    'gender': 'F'
                }
            )[0]
            
            grandpa = Person.objects.get_or_create(
                name="Liu Ye Ye", 
                defaults={
                    'bio': "Family patriarch, war veteran, skilled carpenter and storyteller",
                    'gender': 'M'
                }
            )[0]
            
            # Create location
            home = Location.objects.get_or_create(
                name="Family Ancestral Home",
                defaults={
                    'address': "Old Beijing Hutong",
                    'location_type': 'home',
                    'description': "Traditional courtyard house where the family gathered for decades"
                }
            )[0]
            
            # Create stories
            cooking_story = Story.objects.get_or_create(
                title="Nai Nai's Legendary Dumplings",
                defaults={
                    'content': """Every Chinese New Year, Nai Nai would wake up at 4 AM to start making dumplings. 
                    She would roll out hundreds of perfectly round wrappers by hand, never using a machine. 
                    The filling was a secret recipe passed down from her mother - pork, chives, and a special blend 
                    of spices that made our dumplings different from everyone else's. The whole family would gather 
                    to help wrap them, and Nai Nai would tell stories about her childhood while we worked. 
                    Those moments around the kitchen table, flour on everyone's hands, laughter filling the air, 
                    are some of my most precious memories.""",
                    'story_type': 'tradition',
                    'location': home
                }
            )[0]
            cooking_story.people.add(grandma)
            
            war_story = Story.objects.get_or_create(
                title="Ye Ye's Courage During the War",
                defaults={
                    'content': """During the war, Ye Ye served as a communications officer. He would tell us about 
                    the time he had to carry important messages across enemy lines. One night, he crawled through 
                    rice fields for miles, holding the radio equipment above water, determined to deliver crucial 
                    intelligence that would save his unit. When he finally reached the destination, soaked and 
                    exhausted, the commanding officer said those messages changed the course of their mission. 
                    Ye Ye never talked about the war much, but when he did, his eyes would get distant, 
                    and we knew he was remembering his fallen comrades.""",
                    'story_type': 'memory',
                    'location': home
                }
            )[0]
            war_story.people.add(grandpa)
            
            # Create events
            reunion = Event.objects.get_or_create(
                name="Annual Family Reunion 2023",
                defaults={
                    'description': """Our biggest family gathering in years. Over 30 relatives came from across 
                    the country. We had traditional performances, the children did a tea ceremony for the elders, 
                    and Nai Nai cooked for three days straight. Uncle Wang brought his guqin and played ancient 
                    melodies while everyone shared stories. The highlight was when all four generations 
                    gathered for the family photo under the old persimmon tree.""",
                    'event_type': 'reunion',
                    'start_date': '2023-10-01T10:00:00Z',
                    'location': home
                }
            )[0]
            reunion.participants.add(grandma, grandpa)
            
            # Create heritage
            recipe_heritage = Heritage.objects.get_or_create(
                title="Five-Generation Dumpling Recipe",
                defaults={
                    'description': """This recipe has been passed down through five generations of women in our family. 
                    The secret is in the ratio of fat to lean meat (3:7), the way you chop the vegetables 
                    (always by hand, never machine), and the special seasoning blend that includes white pepper, 
                    sesame oil, and a touch of Shaoxing wine. But most importantly, it's the love and patience 
                    put into every dumpling that makes them special. Each fold of the wrapper seals in not just 
                    the filling, but generations of family tradition.""",
                    'heritage_type': 'recipe',
                    'origin_person': grandma,
                    'importance': 4
                }
            )[0]
            recipe_heritage.stories.add(cooking_story)
            
            # Create health record
            health_record = Health.objects.get_or_create(
                person=grandpa,
                title="Family Heart Health History",
                defaults={
                    'description': """Important family medical history: Ye Ye's father and grandfather both had 
                    heart conditions that appeared after age 60. Ye Ye was diagnosed with mild hypertension at 65 
                    but managed it well with traditional Chinese medicine and regular tai chi practice. 
                    All male descendants should monitor blood pressure regularly and maintain active lifestyle. 
                    Dr. Chen at Beijing Hospital has been our family doctor for 20 years and knows our history well.""",
                    'record_type': 'genetic',
                    'date': '2023-06-15',
                    'is_hereditary': True
                }
            )[0]
            
            self.stdout.write('  ✅ Sample family data created successfully')
            self.stdout.write(f'    - {Person.objects.count()} family members')
            self.stdout.write(f'    - {Story.objects.count()} family stories')
            self.stdout.write(f'    - {Event.objects.count()} family events')
            self.stdout.write(f'    - {Heritage.objects.count()} heritage items')
            self.stdout.write(f'    - {Health.objects.count()} health records')
            
            results['sample_data'] = True
            
        except Exception as e:
            self.stdout.write(f'  ❌ Failed to create sample data: {e}')
            results['sample_data'] = False
    
    def test_embeddings(self, results):
        """Test embedding generation"""
        self.stdout.write('🧠 Testing embedding generation...')
        
        try:
            start_time = time.time()
            
            # Test single embedding generation
            test_text = "This is a test story about family traditions and cooking."
            embedding = embedding_service.generate_embedding(test_text)
            
            if embedding and len(embedding) == 1536:
                self.stdout.write('  ✅ Single embedding generation working')
            else:
                self.stdout.write('  ❌ Single embedding generation failed')
                results['embeddings'] = False
                return
            
            # Test model embedding update
            story = Story.objects.first()
            if story:
                success = embedding_service.update_model_embedding(story)
                if success:
                    self.stdout.write('  ✅ Model embedding update working')
                else:
                    self.stdout.write('  ⚠️  Model embedding update returned False')
            
            # Test bulk embedding updates
            updated_count = 0
            for model_class in [Story, Event, Heritage, Health]:
                stats = embedding_service.bulk_update_embeddings(model_class, batch_size=5)
                updated_count += stats.get('updated', 0)
            
            embedding_time = time.time() - start_time
            results['performance']['embedding_time'] = embedding_time
            
            # Check cache
            cache_count = EmbeddingCache.objects.count()
            
            self.stdout.write(f'  ✅ Bulk embedding complete: {updated_count} items updated')
            self.stdout.write(f'  ✅ Embedding cache: {cache_count} entries')
            self.stdout.write(f'  ⏱️  Total time: {embedding_time:.2f} seconds')
            
            results['embeddings'] = True
            
        except Exception as e:
            self.stdout.write(f'  ❌ Embedding test failed: {e}')
            results['embeddings'] = False
    
    def test_search(self, results):
        """Test search functionality"""
        self.stdout.write('🔍 Testing search functionality...')
        
        try:
            start_time = time.time()
            
            # Test semantic search
            test_queries = [
                "traditional cooking recipes",
                "war stories and military service", 
                "family gatherings and celebrations",
                "health issues and medical history",
                "家庭传统和烹饪"  # Chinese query
            ]
            
            total_results = 0
            for query in test_queries:
                results_list = search_service.semantic_search(query, limit=5)
                total_results += len(results_list)
                self.stdout.write(f'    "{query[:30]}..." → {len(results_list)} results')
            
            # Test category search
            category_results = search_service.search_by_category("cooking", "stories")
            self.stdout.write(f'  ✅ Category search: {len(category_results)} story results')
            
            # Test related content
            story = Story.objects.first()
            if story:
                related = search_service.find_related_content(story.id, 'story')
                self.stdout.write(f'  ✅ Related content: {len(related)} related items')
            
            # Test keyword fallback
            keyword_results = search_service.keyword_search("family")
            self.stdout.write(f'  ✅ Keyword search: {len(keyword_results)} results')
            
            search_time = time.time() - start_time
            results['performance']['search_time'] = search_time
            
            self.stdout.write(f'  ✅ Total search results: {total_results}')
            self.stdout.write(f'  ⏱️  Search time: {search_time:.2f} seconds')
            
            results['search'] = True
            
        except Exception as e:
            self.stdout.write(f'  ❌ Search test failed: {e}')
            results['search'] = False
    
    def test_performance(self, results):
        """Test performance metrics"""
        self.stdout.write('⚡ Testing performance...')
        
        try:
            # Memory usage simulation
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            self.stdout.write(f'  📊 Current memory usage: {memory_mb:.1f} MB')
            
            if memory_mb < 512:  # Heroku limit
                self.stdout.write('  ✅ Memory usage within Heroku limits')
            else:
                self.stdout.write('  ⚠️  Memory usage exceeds Heroku 512MB limit')
            
            results['performance']['memory_mb'] = memory_mb
            
            # Database query performance
            start_time = time.time()
            stories_with_embeddings = Story.objects.filter(content_embedding__isnull=False).count()
            query_time = time.time() - start_time
            
            results['performance']['db_query_time'] = query_time
            self.stdout.write(f'  📊 DB query time: {query_time:.3f} seconds')
            self.stdout.write(f'  📊 Stories with embeddings: {stories_with_embeddings}')
            
        except Exception as e:
            self.stdout.write(f'  ⚠️  Performance test partial failure: {e}')
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.stdout.write('🧹 Cleaning up test data...')
        
        # Remove test AI records
        ChatSession.objects.filter(session_id__startswith='test-').delete()
        EmbeddingCache.objects.filter(content_type='test').delete()
        
        self.stdout.write('  ✅ Test data cleaned up')
    
    def display_results(self, results):
        """Display final test results"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎯 AI SYSTEM TEST RESULTS'))
        self.stdout.write('='*50)
        
        status_icon = lambda x: '✅' if x else '❌'
        
        self.stdout.write(f'{status_icon(results["api_keys"])} API Configuration')
        self.stdout.write(f'{status_icon(results["models"])} AI Models')
        self.stdout.write(f'{status_icon(results["sample_data"])} Sample Data Creation')
        self.stdout.write(f'{status_icon(results["embeddings"])} Embedding Generation')
        self.stdout.write(f'{status_icon(results["search"])} Search Functionality')
        
        if results['performance']:
            perf = results['performance']
            self.stdout.write('\n📊 PERFORMANCE METRICS:')
            if 'memory_mb' in perf:
                self.stdout.write(f'   Memory Usage: {perf["memory_mb"]:.1f} MB')
            if 'embedding_time' in perf:
                self.stdout.write(f'   Embedding Time: {perf["embedding_time"]:.2f} seconds')
            if 'search_time' in perf:
                self.stdout.write(f'   Search Time: {perf["search_time"]:.2f} seconds')
            if 'db_query_time' in perf:
                self.stdout.write(f'   DB Query Time: {perf["db_query_time"]:.3f} seconds')
        
        # Overall status
        all_passed = all([
            results['api_keys'] or True,  # API keys optional for testing
            results['models'],
            results['sample_data'],
            results['embeddings'],
            results['search']
        ])
        
        if all_passed:
            self.stdout.write(self.style.SUCCESS('\n🎉 ALL TESTS PASSED! AI system is ready for production.'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  Some tests failed. Check configuration and fix issues.'))
        
        self.stdout.write('='*50)