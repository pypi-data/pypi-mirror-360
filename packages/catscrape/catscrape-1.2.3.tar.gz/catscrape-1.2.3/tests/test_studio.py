from catscrape import Studio
import time

# VARIABLES

TEST_STUDIO_ID = 36086387

# TESTS

def test_studio_curators():
    # Get curators
    studio = Studio(TEST_STUDIO_ID)
    curators = studio.get_curators()

    print(curators)

    # Assertions
    assert "MLTGeniusCoder" in curators or "NathProductions24" in curators

def test_studio_curator_count():
    # Get curator count
    studio = Studio(TEST_STUDIO_ID)
    curator_count = studio.curator_count()

    print(curator_count)

    # Assertions
    assert curator_count > 10

def test_studio_cache():
    # Get the curator count
    studio = Studio(TEST_STUDIO_ID)
    studio.get_curators()

    # Run get_curators again. It should return instantly
    start = time.time()
    studio.get_curators()
    total = time.time() - start

    # Assertions
    assert total < 0.2

def test_studio_curator_count_cache():
    # Test running curator_count function to cache
    studio = Studio(TEST_STUDIO_ID)
    studio.curator_count()

    # Run get_curators again. It should return instantly
    start = time.time()
    studio.get_curators()
    total = time.time() - start

    # Assertions
    assert total < 0.2