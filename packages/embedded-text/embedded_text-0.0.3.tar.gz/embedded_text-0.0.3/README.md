# embedded-text

Tool for extracting embedded text data in python script.

## Requirement

  - Python >= 3.9
  - pip3

## Usage

  1. Install

    ```
    % pip install embedded-text
    ```

  2. import in your script

     ```
     import embedded_text
     ```

  3. Embeddig text data at the end of your script with head/tail lines

    ```
    if False:
        ############# Embedded Code Start #######################
    
        #!/usr/bin/env python3
    
        def main():
            print ('This is the sample : ____OUTPUT_WORDS____')
            
            if __name__ == '__main__':
                main()
            
        ############# Embedded Code End #######################
    ``` 

   4. Initialize class with regular expression of head/tail lines

     ```
         s_pttrn = r'\s*#{5,}\s*Embedded\s+Code\s+Start\s*#{5,}',
         e_pttrn = r'\s*#{5,}\s*Embedded\s+Code\s+End\s*#{5,}'},
         extractor = EmbeddedText(s_marker=s_pttrn,
                                  e_marker=e_pttrn, ...)
     ```

   5. You can do iterator access by EmbeddedText.lines()

      ```
            for line in extractor.lines(input_path=None):
                sys.stdout.write(line)
      ```

   5. You can save to other file by EmbeddedText.dump()

      ```
            extractor.dump(output_path, input_path=None)
      ```

     It is possible to apply the keyword replacement and text filtering. You can see the example in "main()" function in "embedded_text.py"

## Author
    Nanigashi Uji (53845049+nanigashi-uji@users.noreply.github.com)
    Nanigashi Uji (4423013-nanigashi_uji@users.noreply.gitlab.com)
