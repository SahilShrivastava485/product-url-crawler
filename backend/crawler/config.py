import os

# Concurrency control
CONCURRENT_REQUESTS = 5
MAX_PRODUCT_LINKS = 100

# Redis and Celery settings
CELERY_BROKER = "redis://localhost:6379/0"
CELERY_BACKEND = "redis://localhost:6379/0"

# User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)"
]

# Product page patterns
COMMON_PATTERNS = [
    r"/product/",
    r"/products/",
    r"/item/",
    r"/items/",
    r"/p/",
    r"/dp/",
    r"/gp/product/",
    r"/store/products/",
    r"/shop/",
    r"/catalog/product/",
    r"/sku/",
    r"/pid/",
    r"/itm/",
    r"/goods/",
    r"/app/",
    r"/collections/",
    r"/view/",
    r"/productId="
]

COMMON_URLS =[
    "https://www.flipkart.com/samsung-galaxy-book3-core-i7-13th-gen-16-gb-512-gb-ssd-windows-11-home-thin-light-laptop/p/itmf5efb3b1c35fa?otracker=undefined_footer",
    "https://www.amazon.in/Vinayaka-Fab-Decorative-Rectangular-Cushion/dp/B09PBWWS73/?_encoding=UTF8&pd_rd_w=CYe1f&content-id=amzn1.sym.2f52b549-32d2-403f-968d-ecac7ca5a83f&pf_rd_p=2f52b549-32d2-403f-968d-ecac7ca5a83f&pf_rd_r=XZ7MEM20H45JNW15ZCZZ&pd_rd_wg=r0SMQ&pd_rd_r=8f5351cc-7705-4195-aaaf-95a88b025a30&ref_=pd_hp_d_btf_ls_gwc_pc_en2_",
    "https://www.bigbasket.com/pd/40320545/precia-classic-bengali-rasmalai-125-g/?nc=cl-prod-list&t_pos_sec=1&t_pos_item=1&t_s=Classic%2520Bengali%2520Rasmalai",
    "https://www.lenskart.com/vincent-chase-vc-5158/p-c133-sunglasses.html",
    "https://www.myntra.com/shirts/wrogn/wrogn-pure-cotton-slim-fit-casual-shirt/25827226/buy",
    "https://www.snapdeal.com/product/aadi-black-casual-shoes/638773718836",
    "https://www.nykaa.com/l-oreal-paris-hyaluron-pure-72h-purifying-shampoo/p/18755140?productId=18755140&pps=1&skuId=18755135"
]