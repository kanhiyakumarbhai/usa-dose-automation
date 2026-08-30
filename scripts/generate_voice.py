name: USA Dose Daily Automation

on:
  workflow_dispatch:

  schedule:
    # 2 Shorts every day
    # 00:30 UTC = 06:00 AM IST
    - cron: "30 0 * * *"

    # 12:30 UTC = 06:00 PM IST
    - cron: "30 12 * * *"

permissions:
  contents: write


jobs:

  create-and-upload:

    runs-on: ubuntu-latest

    steps:

      # ==================================================
      # CHECKOUT
      # ==================================================

      - name: Checkout repository
        uses: actions/checkout@v4


      # ==================================================
      # PYTHON
      # ==================================================

      - name: Setup Python
        uses: actions/setup-python@v5

        with:
          python-version: "3.12"


      # ==================================================
      # SYSTEM PACKAGES
      # ==================================================

      - name: Install FFmpeg and eSpeak
        run: |

          sudo apt-get update

          sudo apt-get install -y \
            ffmpeg \
            espeak-ng


      # ==================================================
      # PYTHON PACKAGES
      # ==================================================

      - name: Install Python packages
        run: |

          python -m pip install --upgrade pip

          pip install elevenlabs
          pip install requests
          pip install google-genai

          pip install google-api-python-client
          pip install google-auth
          pip install google-auth-oauthlib
          pip install google-auth-httplib2


      # ==================================================
      # CHECK PROJECT FILES
      # ==================================================

      - name: Check project files
        run: |

          echo "================================"
          echo "PROJECT FILES"
          echo "================================"

          ls -lah

          echo ""
          echo "Scripts:"
          ls -lah scripts || true

          echo ""

          if [ ! -f "scripts/generate_script.py" ]; then
            echo "ERROR: scripts/generate_script.py not found"
            exit 1
          fi

          if [ ! -f "scripts/generate_voice.py" ]; then
            echo "ERROR: scripts/generate_voice.py not found"
            exit 1
          fi

          if [ ! -f "create_video.py" ]; then
            echo "ERROR: create_video.py not found"
            exit 1
          fi

          if [ ! -f "download_clips.py" ]; then
            echo "ERROR: download_clips.py not found"
            exit 1
          fi

          if [ ! -f "upload_video.py" ]; then
            echo "ERROR: upload_video.py not found"
            exit 1
          fi

          echo ""
          echo "All required files found."


      # ==================================================
      # GENERATE DAILY SCRIPT
      # ==================================================

      - name: Generate daily USA Dose script

        env:

          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}

        run: |

          echo "================================"
          echo "GENERATING DAILY SCRIPT"
          echo "================================"

          python scripts/generate_script.py

          if [ ! -s "daily_script.txt" ]; then
            echo "ERROR: daily_script.txt is empty"
            exit 1
          fi

          if [ ! -s "video_title.txt" ]; then
            echo "ERROR: video_title.txt is empty"
            exit 1
          fi

          if [ ! -s "video_hashtags.txt" ]; then
            echo "ERROR: video_hashtags.txt is empty"
            exit 1
          fi

          echo ""
          echo "SCRIPT GENERATED"

          echo ""
          echo "SCRIPT:"
          cat daily_script.txt

          echo ""
          echo "TITLE:"
          cat video_title.txt

          echo ""
          echo "HASHTAGS:"
          cat video_hashtags.txt


      # ==================================================
      # GENERATE LAURA FEMALE VOICE
      # ==================================================

      - name: Generate Laura Female Voice

        env:

          # IMPORTANT:
          # Multi-key failover

          ELEVENLABS_API_KEY_1: ${{ secrets.ELEVENLABS_API_KEY }}

          ELEVENLABS_API_KEY_2: ${{ secrets.ELEVENLABS_API_KEY_2 }}

          ELEVENLABS_API_KEY_3: ${{ secrets.ELEVENLABS_API_KEY_3 }}

          ELEVENLABS_API_KEY_4: ${{ secrets.ELEVENLABS_API_KEY_4 }}

          ELEVENLABS_API_KEY_5: ${{ secrets.ELEVENLABS_API_KEY_5 }}

        run: |

          echo "================================"
          echo "GENERATING FEMALE VOICE"
          echo "================================"

          python scripts/generate_voice.py

          if [ ! -f "voice.mp3" ]; then

            echo ""
            echo "ERROR: voice.mp3 was not created"

            exit 1

          fi

          echo ""
          echo "VOICE CREATED"

          ls -lh voice.mp3


      # ==================================================
      # DOWNLOAD MOVING STOCK CLIPS
      # ==================================================

      - name: Download moving stock clips

        env:

          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}

        run: |

          echo "================================"
          echo "DOWNLOADING MOVING STOCK CLIPS"
          echo "================================"

          rm -rf clips

          mkdir -p clips

          python download_clips.py

          echo ""
          echo "DOWNLOADED CLIPS:"

          find clips \
            -maxdepth 1 \
            -type f \
            -print || true

          CLIP_COUNT=$(
            find clips \
            -maxdepth 1 \
            -type f \
            \( \
              -name "*.mp4" \
              -o \
              -name "*.mov" \
            \) \
            | wc -l
          )

          echo ""
          echo "Clip count: $CLIP_COUNT"

          if [ "$CLIP_COUNT" -lt 1 ]; then

            echo ""
            echo "ERROR: No moving video clips downloaded"

            exit 1

          fi


      # ==================================================
      # CREATE HD VIDEO
      # ==================================================

      - name: Create USA Dose Short

        run: |

          echo "================================"
          echo "CREATING USA DOSE SHORT"
          echo "================================"

          python create_video.py

          if [ ! -f "usa_dose_short.mp4" ]; then

            echo ""
            echo "ERROR: usa_dose_short.mp4 was not created"

            exit 1

          fi

          echo ""
          echo "FINAL VIDEO CREATED:"

          ls -lh usa_dose_short.mp4

          echo ""
          echo "VIDEO INFORMATION:"

          ffprobe \
            -v error \
            -select_streams v:0 \
            -show_entries stream=codec_name,width,height,r_frame_rate \
            -of default=noprint_wrappers=1 \
            usa_dose_short.mp4 || true


      # ==================================================
      # UPLOAD TO YOUTUBE
      # ==================================================

      - name: Upload Short to YouTube

        env:

          YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}

          YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}

          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}

        run: |

          echo "================================"
          echo "UPLOADING SHORT TO YOUTUBE"
          echo "================================"

          python upload_video.py


      # ==================================================
      # SAVE GENERATED FILES
      # ==================================================

      - name: Save generated files

        run: |

          git config user.name "USA Dose Bot"

          git config user.email \
            "actions@users.noreply.github.com"

          git add \
            daily_script.txt \
            video_title.txt \
            video_hashtags.txt \
            voice.mp3 \
            usa_dose_short.mp4

          if git diff --cached --quiet; then

            echo ""
            echo "No changes to commit."

          else

            git commit \
              -m "Daily USA Dose Short"

            git push

          fi


      # ==================================================
      # COMPLETE
      # ==================================================

      - name: Automation complete

        run: |

          echo ""
          echo "================================"
          echo "USA DOSE AUTOMATION COMPLETE"
          echo "================================"

          echo "Daily Shorts: 2"

          echo "Voice: Laura"

          echo "Voice: Female"

          echo "Accent: American"

          echo "HD: 1080x1920"

          echo "Moving clips: YES"

          echo "Captions: YES"

          echo "Unique title: YES"

          echo "Hashtags: 7+"

          echo "YouTube: PRIVATE"

          echo "Multi API failover: ACTIVE"

          echo "================================"
