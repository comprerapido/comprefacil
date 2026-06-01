<?php
/**
 * Proxy de Imagem Simples para Radar Ninja
 * Contorna bloqueios de hotlink do Mercado Livre
 */
if (isset($_GET['url'])) {
    $url = $_GET['url'];
    
    // Validação básica para segurança
    if (strpos($url, 'mlstatic.com') !== false) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
        curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        $data = curl_exec($ch);
        $contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
        curl_close($ch);
        
        header("Content-Type: $contentType");
        header("Cache-Control: public, max-age=86400");
        echo $data;
        exit;
    }
}
header("HTTP/1.1 404 Not Found");
?>
