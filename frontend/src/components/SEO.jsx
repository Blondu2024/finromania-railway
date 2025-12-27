import { Helmet } from 'react-helmet-async';

export const SEO = ({
  title = 'FinRomania - Platformă Educațională de Trading',
  description = 'Prima platformă educațională de trading din România. Învață trading gratuit cu 17 lecții interactive, date live BVB, AI Advisor, și instrumente profesionale - 100% în română!',
  keywords = 'trading romania, bursa bucuresti, bvb, invatare trading, cursuri trading gratuite, actiuni romanesti, analiza tehnica, investitii romania, educational trading',
  image = 'https://finromania-3.preview.emergentagent.com/og-image.jpg',
  url = 'https://finromania-3.preview.emergentagent.com',
  type = 'website',
  author = 'FinRomania',
  publishedTime,
  modifiedTime,
  section,
  tags = []
}) => {
  const siteTitle = 'FinRomania';
  const fullTitle = title.includes(siteTitle) ? title : `${title} | ${siteTitle}`;
  
  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="title" content={fullTitle} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content={author} />
      <link rel="canonical" href={url} />
      
      {/* Language & Locale */}
      <html lang="ro" />
      <meta httpEquiv="content-language" content="ro" />
      <meta name="language" content="Romanian" />
      <meta property="og:locale" content="ro_RO" />
      
      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:site_name" content={siteTitle} />
      <meta property="og:locale" content="ro_RO" />
      
      {/* Article specific */}
      {type === 'article' && publishedTime && (
        <meta property="article:published_time" content={publishedTime} />
      )}
      {type === 'article' && modifiedTime && (
        <meta property="article:modified_time" content={modifiedTime} />
      )}
      {type === 'article' && section && (
        <meta property="article:section" content={section} />
      )}
      {type === 'article' && tags.length > 0 && tags.map((tag, idx) => (
        <meta key={idx} property="article:tag" content={tag} />
      ))}
      
      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={url} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />
      <meta name="twitter:creator" content="@FinRomania" />
      
      {/* Additional SEO */}
      <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
      <meta name="googlebot" content="index, follow" />
      <meta name="bingbot" content="index, follow" />
      
      {/* Mobile Optimization */}
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
      <meta name="theme-color" content="#2563eb" />
      <meta name="mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="default" />
      <meta name="apple-mobile-web-app-title" content={siteTitle} />
      
      {/* Geo Tags (Romania specific) */}
      <meta name="geo.region" content="RO" />
      <meta name="geo.placename" content="Romania" />
      <meta name="geo.position" content="45.9432;24.9668" />
      <meta name="ICBM" content="45.9432, 24.9668" />
    </Helmet>
  );
};

export default SEO;
