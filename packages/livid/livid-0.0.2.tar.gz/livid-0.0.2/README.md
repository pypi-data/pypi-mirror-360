## Raison d'etre

GUID and UUID are not good ID schemes for the web because they are not designed for human consumption.
They are too long and too hard to type, therefore not adequate for a URL.
Youtube solved this problem perfectly with their 11-character video IDs, which:

- are short,
- are as easy to type as is realistic to hope for, and
- contain a lot of information in them.

Now you wish to use the same scheme in your application.

- Below is a specification. It is identical to what YouTube does, as far as we know. Let us call it "Livid".
- This project contains implementations of the spec:
    - in Dart (TODO)
    - in Javascript (TODO)
    - in Python

## Livid specification

### Length and alphabet

* **11 characters** long (commonly constant, though not formally guaranteed) ([webapps.stackexchange.com][1]).
* Characters drawn from a **URL-safe Base64** set `A–Z a–z 0–9 - _` (64 possibilities) ([webapps.stackexchange.com][1]).

### Bit structure and payload

* Encodes a **64-bit integer** payload.
* 11 Base64 characters ≈ 66 bits; only about **64 bits** carry payload.
* The **last character** is restricted to 16 possible values to zero out unused bits.

The regular expression pattern for valid IDs is `[A-Za-z0-9_-]{10}[AEIMQUYcgkosw048]`.

### Encoding process

1. Generate a **random 64-bit unsigned integer**.
2. Encode in Base64, producing an 11-character string.
   - Standard Base64 uses `+/`; we replace `/` with `-` and `+` with `_` for URL safety.
   - No padding (`=`) is used, as the length is fixed ([stackoverflow.com][2], [wiki.archiveteam.org][3], [webapps.stackexchange.com][1]).
3. If the integer collides with an existing ID, regenerate. Collisions are extremely rare in such a large space.

### Collision and randomness strategy

- IDs are **randomly generated**, not sequential, to avoid enumeration, scraping, and privacy leaks ([reddit.com][4]).
- Collision-checking ensures uniqueness.

### Validity and guaranteed uniqueness

- Though the 11-char format is stable, there's **no official commitment** to keep it permanently ([webapps.stackexchange.com][1]).
- To validate or test an ID, you must query the existing data ([webapps.stackexchange.com][1]).

---

### Summary table

| Feature                   | Description                               |
| ------------------------- | ----------------------------------------- |
| **Length**                | Exactly 11 chars                          |
| **Character set**         | `[A–Z][a–z][0–9][- _]`                    |
| **Encoded data**          | 64-bit + 2 unused bits                    |
| **End-char restrictions** | Only 16 values (last 2 bits zeroed)       |
| **Generation method**     | Random + Base64 URL-safe encoding         |
| **Collision handling**    | Check uniqueness, retry on conflict       |
| **Validation**            | Query the server/API                  |
| **Guarantee**             | No official guarantee on format stability |

---

[1]: https://webapps.stackexchange.com/questions/54443/format-for-id-of-youtube-video?utm_source=chatgpt.com "Format for ID of YouTube video - Web Applications Stack Exchange"
[2]: https://stackoverflow.com/questions/73276694/youtube-video-id-algorithm?utm_source=chatgpt.com "YouTube Video ID Algorithm - javascript - Stack Overflow"
[3]: https://wiki.archiveteam.org/index.php/YouTube/Technical_details?utm_source=chatgpt.com "YouTube/Technical details - Archiveteam"
[4]: https://www.reddit.com/r/learnprogramming/comments/gx0jvr/how_does_youtube_manages_video_ids_how_to/?utm_source=chatgpt.com "How does YouTube manages video IDs? How to replicate ... - Reddit"
