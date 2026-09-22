package main

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"
)

type URL struct {
	ID          string    `json:"id"`
	OriginalUrl string    `json:"original_url"`
	ShortUrl    string    `json:"short_url"`
	CreatedAt   time.Time `json:"created_at"`
}

var urlDb = make(map[string]URL)
var mu sync.Mutex

func generateShortUrl(OrigianUrl string) string {
	hasher := md5.New()
	hasher.Write([]byte(OrigianUrl))
	data := hasher.Sum(nil)
	hash := hex.EncodeToString(data)
	return hash[:8]
}

func createUrl(originalUrl string) URL {
	mu.Lock()
	defer mu.Unlock()
	shortUrl := generateShortUrl(originalUrl)
	id := shortUrl
	urlDb[id] = URL{
		ID:          id,
		OriginalUrl: originalUrl,
		ShortUrl:    shortUrl,
		CreatedAt:   time.Now(),
	}
	return urlDb[id]
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Println("here in handler")
}

func shortUrlHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Println("here in shortUrlHandler")
	var data struct {
		OriginalUrl string `json:"original_url"`
	}
	err := json.NewDecoder(r.Body).Decode(&data)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	shortUrl := createUrl(data.OriginalUrl)
	response := struct {
		ShortUrl string `json:"short_url"`
	}{
		ShortUrl: shortUrl.ShortUrl,
	}
	w.Header().Set("Content-Type", "application/json")
	err = json.NewEncoder(w).Encode(response)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func main() {
	http.HandleFunc("/shorten", shortUrlHandler)
	fmt.Println("Starting server")
	err := http.ListenAndServe(":3002", nil)
	if err != nil {
		fmt.Println(err)
	}
}
